import unittest
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio
import time
from authorize_phone import (
    main, 
    update_authorization_state, 
    get_last_code_sent_time, 
    update_last_code_sent_time, 
    validate_phone_number
)

class TestAuthorizePhone(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        # Mock DB connection for all tests
        self.db_patcher = patch('authorize_phone.get_db_connection')
        self.mock_db = self.db_patcher.start()
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value.__enter__.return_value = self.mock_cursor
        self.mock_db.return_value.__enter__.return_value = self.mock_conn

        # Mock time for consistent testing
        self.time_patcher = patch('time.time')
        self.mock_time = self.time_patcher.start()
        self.mock_time.return_value = 1234567890

    def tearDown(self):
        self.db_patcher.stop()
        self.time_patcher.stop()
        self.loop.close()

    @patch('authorize_phone.TelegramClient')
    async def async_test_send_code(self, MockTelegramClient):
        # Setup mock client
        mock_client = MockTelegramClient.return_value
        mock_client.connect = AsyncMock()
        mock_client.send_code_request = AsyncMock()
        mock_client.is_user_authorized = AsyncMock(return_value=False)
        mock_client.disconnect = AsyncMock()

        # Mock database responses
        self.mock_cursor.fetchone.return_value = [0]  # Last code sent time
        self.mock_cursor.execute.return_value = True
        self.mock_conn.commit.return_value = None

        # Mock phone number validation
        with patch('authorize_phone.validate_phone_number', return_value=True):
            result = await main(12345, "api_hash", "+1234567890", "send_code")
            self.assertTrue(result)
            mock_client.send_code_request.assert_called_once_with("+1234567890")

    def test_send_code(self):
        self.loop.run_until_complete(self.async_test_send_code())

    @patch('authorize_phone.TelegramClient')
    async def async_test_verify_code(self, MockTelegramClient):
        # Setup mock client
        mock_client = MockTelegramClient.return_value
        mock_client.connect = AsyncMock()
        mock_client.sign_in = AsyncMock()
        mock_client.disconnect = AsyncMock()

        # Mock database responses
        self.mock_cursor.execute.return_value = True
        self.mock_conn.commit.return_value = None

        # Mock phone number validation
        with patch('authorize_phone.validate_phone_number', return_value=True):
            result = await main(12345, "api_hash", "+1234567890", "verify_code", "123456")
            self.assertTrue(result)
            mock_client.sign_in.assert_called_once_with("+1234567890", "123456")

    def test_verify_code(self):
        self.loop.run_until_complete(self.async_test_verify_code())

    def test_validate_phone_number(self):
        valid_numbers = ["+1234567890", "+442071234567", "+12025550179"]
        invalid_numbers = ["invalid_number", "12345", "+123", "++1234567890"]
        
        mock_parsed = MagicMock()
        mock_parsed.national_number = 1234567890

        with patch('phonenumbers.parse', return_value=mock_parsed) as mock_parse, \
             patch('phonenumbers.is_valid_number', return_value=True) as mock_is_valid:
            
            for number in valid_numbers:
                with self.subTest(number=number):
                    self.assertTrue(validate_phone_number(number))
                    
            mock_is_valid.return_value = False
            for number in invalid_numbers:
                with self.subTest(number=number):
                    self.assertFalse(validate_phone_number(number))

    def test_update_authorization_state(self):
        update_authorization_state("+1234567890", "authorized")
        self.mock_cursor.execute.assert_called_once_with(
            "UPDATE settings SET authorization_state=%s WHERE authorized_phone_number=%s",
            ("authorized", "+1234567890")
        )
        self.mock_conn.commit.assert_called_once()

    def test_get_last_code_sent_time(self):
        expected_time = 1234567890
        self.mock_cursor.fetchone.return_value = [expected_time]
        
        result = get_last_code_sent_time("+1234567890")
        self.assertEqual(result, expected_time)
        self.mock_cursor.execute.assert_called_once_with(
            "SELECT last_code_sent_time FROM settings WHERE authorized_phone_number=%s",
            ("+1234567890",)
        )

    def test_update_last_code_sent_time(self):
        update_last_code_sent_time("+1234567890")
        self.mock_cursor.execute.assert_called_once_with(
            "UPDATE settings SET last_code_sent_time=%s WHERE authorized_phone_number=%s",
            (1234567890, "+1234567890")
        )
        self.mock_conn.commit.assert_called_once()

if __name__ == "__main__":
    unittest.main()