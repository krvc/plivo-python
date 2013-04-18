import unittest
import os
import random
import string

import plivo

try:
    from auth_secrets import AUTH_ID, AUTH_TOKEN
    from auth_secrets import DEFAULT_FROM_NUMBER, DEFAULT_TO_NUMBER
except ImportError:
    AUTH_ID, AUTH_TOKEN = os.getenv("AUTH_ID"), os.getenv("AUTH_TOKEN")
    DEFAULT_FROM_NUMBER = os.getenv("DEFAULT_FROM_NUMBER")
    DEFAULT_TO_NUMBER = os.getenv("DEFAULT_TO_NUMBER")
    if not (AUTH_ID and AUTH_TOKEN and
            DEFAULT_FROM_NUMBER and DEFAULT_TO_NUMBER):
        raise Exception("Create a auth_secrets.py file or set AUTH_ID "
                        "AUTH_TOKEN, DEFAULT_TO_NUMBER, DEFAULT_FROM_NUMBER "
                        "as environ values.")

client = None
random_letter = lambda: random.choice(string.ascii_letters)
random_string = lambda len: ''.join(random_letter() for i in range(len))


class PlivoTest(unittest.TestCase):
    "Adds a plivo client in setup"
    def setUp(self):
        self.client = get_client(AUTH_ID, AUTH_TOKEN)
        self.some_timezones = ['Pacific/Apia', 'Pacific/Midway']

    def check_status_and_keys(self, status, valid_keys, response):
        self.assertEqual(status, response[0])
        json_response = response[1]
        for key in valid_keys:
            self.assertTrue(key in json_response)


class TestAccounts(PlivoTest):
    def test_get_account(self):
        response = self.client.get_account()
        self.assertEqual(200, response[0])
        valid_keys = ["account_type", "address", "auth_id", "auto_recharge",
                      "cash_credits", "city", "created", "enabled"]
        json_response = response[1]
        for key in valid_keys:
            self.assertTrue(key in json_response)

    def test_modify_account_name(self):
        random_name = random_string(10)
        params = {'name': random_name}
        self.client.modify_account(params)

        response = self.client.get_account()
        self.assertEqual(random_name, response[1]['name'])

    def test_modify_account_city(self):
        random_city = random_string(10)
        params = {'city': random_city}
        self.client.modify_account(params)

        response = self.client.get_account()
        self.assertEqual(random_city, response[1]['city'])

    def test_modify_account_address(self):
        random_address = random_string(20)
        params = {'address': random_address}
        self.client.modify_account(params)

        response = self.client.get_account()
        self.assertEqual(random_address, response[1]['address'])

    def test_modify_account_restricted_params(self):
        res = self.client.get_account()[1]

        random_name = random_string(10)
        random_city = random_string(10)
        random_address = random_string(10)
        random_state = random_string(6)

        random_timezone = ''
        if res['timezone'] in self.some_timezones:
            index = self.some_timezones.index(res['timezone'])
            if index != 0:
                random_timezone = self.some_timezones[0]
            else:
                random_timezone = self.some_timezones[1]
        else:
            random_timezone = self.some_timezones[0]

        random_cashcredit = "".join(random.sample('97654', 4))
        while(1):
            if random_cashcredit != res['cash_credits']:
                break
            random_cashcredit = "".join(random.sample('97654', 4))

        params = {
            'name': random_name,
            'city': random_city,
            'address': random_address,
            'account_type': 'dasghfdsg',
            'auth_id': 'gadfgsfsdfdsgs',
            'auto_recharge': not(res['auto_recharge']),
            'cash_credits': random_cashcredit,
            'created': "1952-05-04",
            'enabled': not(res['enabled']),
            'resource_uri': '/akjslsjkls/dsfg',
            'state': random_state,
            'timezone': random_timezone,
        }
        self.client.modify_account(params)

        r = self.client.get_account()[1]

        #These params should be modified
        self.assertEqual(r['name'], params['name'])
        self.assertEqual(r['city'], params['city'])
        self.assertEqual(r['address'], params['address'])
        self.assertEqual(r['state'], params['state'])
        self.assertEqual(r['timezone'], params['timezone'])

        #These params should not be modified
        self.assertEqual(r['account_type'], res['account_type'])
        self.assertEqual(r['auth_id'], res['auth_id'])
        self.assertEqual(r['auto_recharge'], res['auto_recharge'])
        self.assertEqual(r['created'], res['created'])
        self.assertEqual(r['enabled'], res['enabled'])
        self.assertEqual(r['resource_uri'], res['resource_uri'])

        self.assertNotEqual(r['account_type'], params['account_type'])
        self.assertNotEqual(r['auth_id'], params['auth_id'])
        self.assertNotEqual(r['auto_recharge'], params['auto_recharge'])
        self.assertNotEqual(r['created'], params['created'])
        self.assertNotEqual(r['enabled'], params['enabled'])
        self.assertNotEqual(r['resource_uri'], params['resource_uri'])

    def test_get_subaccounts(self):
        response = self.client.get_subaccounts()
        valid_keys = ["meta", "api_id", "objects"]
        self.check_status_and_keys(200, valid_keys, response)

    def test_subaccount_crud(self):
        temp_name = random_string(10)
        response = self.client.create_subaccount(dict(name=temp_name,
                                                 enabled=True))
        self.assertEqual(201, response[0])
        valid_keys = ["auth_id", "api_id", "auth_token"]
        json_response = response[1]
        for key in valid_keys:
            self.assertTrue(key in json_response)
        auth_id = json_response["auth_id"]
        response = self.client.get_subaccount(dict(subauth_id=auth_id))
        self.assertEqual(200, response[0])

        self.client.modify_subaccount({'subauth_id': auth_id,
                                       'name': temp_name,
                                       'enabled': False})
        response = self.client.get_subaccount({'subauth_id': auth_id})[1]
        #check modified details
        self.assertEqual(response['enabled'], False)
        self.assertEqual(response['name'], temp_name)

        response = self.client.delete_subaccount(dict(subauth_id=auth_id))
        self.assertEqual(204, response[0])
        # Deleted sub account should not exist
        response = self.client.get_subaccount({'subauth_id': auth_id})[1]
        self.assertEqual(response['error'], 'not found')


class TestApplication(PlivoTest):
    def test_get_applications(self):
        response = self.client.get_applications()
        valid_keys = ["objects", "api_id", "meta"]
        self.check_status_and_keys(200, valid_keys, response)

    def test_applications_crud(self):
        params = {'answer_url': 'http://localhost.com',
                  'app_name': 'testappname'}
        response = self.client.create_application(params)
        self.assertEqual(201, response[0])

        app_id = response[1]['app_id']
        response = self.client.get_application({'app_id': app_id})
        self.assertEqual(response[1]['app_name'], params['app_name'])
        self.assertEqual(200, response[0])

        new_params = {'app_name': 'some new test name', 'app_id': app_id}
        response = self.client.modify_application(new_params)
        self.assertEqual(202, response[0])

        #check whether app_name modified or not
        response = self.client.get_application({'app_id': app_id})
        self.assertEqual(response[1]['app_name'], new_params['app_name'])

        #delete application
        response = self.client.delete_application({'app_id': app_id})
        self.assertEqual(204, response[0])

        #deleted application should not be available
        response = self.client.get_application({'app_id': app_id})
        self.assertEqual(404, response[0])
        self.assertEqual('not found', response[1]['error'])


class TestEndpoint(PlivoTest):
    def test_get_endpoints(self):
        response = self.client.get_endpoints()
        valid_keys = ["objects", "api_id", "meta"]
        self.check_status_and_keys(200, valid_keys, response)

    def test_endpoint_crud(self):
        params = {'username': 'agdrasg',
                  'password': 'ahfdsgdf',
                  'alias': 'asasddas'}
        response = self.client.create_endpoint(params)
        self.assertEqual(201, response[0])

        endpoint_id = response[1]['endpoint_id']

        response = self.client.get_endpoint({'endpoint_id': endpoint_id})
        self.assertEqual(200, response[0])
        #check created endpoint details
        self.assertEqual(response[1]['alias'], params['alias'])

        #modify endpoint
        new_params = {'alias': 'new alias fasda', 'endpoint_id': endpoint_id}
        response = self.client.modify_endpoint(new_params)
        self.assertEqual(202, response[0])

        #check modified details
        response = self.client.get_endpoint({'endpoint_id': endpoint_id})
        self.assertEqual(response[1]['alias'], new_params['alias'])

        #delete endpoint
        response = self.client.delete_endpoint({'endpoint_id': endpoint_id})
        self.assertEqual(204, response[0])

        #deleted endpoint should not be available
        response = self.client.get_endpoint({'endpoint_id': endpoint_id})
        self.assertEqual(404, response[0])
        self.assertEqual(response[1]['error'], 'not found')


class TestPricing(PlivoTest):
    def test_pricing(self):
        response = self.client.pricing({'country_iso': 'US'})
        valid_keys = ["country", "api_id", 'country_code', 'country_iso',
                      'phone_numbers', 'voice', 'message']
        self.check_status_and_keys(200, valid_keys, response)

    def test_invalid_country(self):
        response = self.client.pricing({'country_iso': 'USSDGF'})
        self.assertTrue("error" in response[1])


class TestRecording(PlivoTest):
    def test_get_all_recordings(self):
        response = self.client.get_recordings()
        valid_keys = ['meta', 'objects', 'api_id']
        self.check_status_and_keys(200, valid_keys, response)


class TestNumber(PlivoTest):
    def test_get_numbers(self):
        response = self.client.get_numbers()
        valid_keys = ['meta', 'objects', 'api_id']
        self.check_status_and_keys(200, valid_keys, response)

    def test_get_number(self):
        response = self.client.get_number({"number": DEFAULT_FROM_NUMBER})
        valid_keys = ["added_on", "api_id", "application", "carrier", "number",
                      "sms_enabled", "voice_enabled"]
        self.check_status_and_keys(nu200, valid_keys, response)
        self.assertEqual(DEFAULT_FROM_NUMBER, response[1]["number"])

    def test_number_crud(self):
        response = self.client.get_number_group({"country_iso": "US"})
        valid_keys = ["meta", "api_id", "objects"]
        self.check_status_and_keys(200, valid_keys, response)
        group_id = response[1]["objects"][0]["group_id"]
        response = self.client.rent_from_number_group({"group_id": group_id})
        valid_keys = ["numbers", "status"]
        self.check_status_and_keys(201, valid_keys, response)
        number = response[1]["numbers"][0]["number"]
        response = self.client.unrent_number({"number": number})


class TestCarrier(PlivoTest):
    def test_incoming_carriers(self):
        response = self.client.get_incoming_carriers()
        valid_keys = ['meta', 'objects', 'api_id']
        self.check_status_and_keys(200, valid_keys, response)

    def test_incoming_carrier_crud(self):
        random_name = random_string(10)
        params = {'name': random_name, 'ip_set': '192.168.1.143'}

        #create incoming carrier
        response = self.client.create_incoming_carrier(params)
        self.assertEqual(201, response[0])
        carrier_id = response[1]['carrier_id']

        #get created carrier and check its details
        response = self.client.get_incoming_carrier({'carrier_id': carrier_id})
        self.assertEqual(200, response[0])
        self.assertEqual(response[1]['name'], params['name'])
        self.assertEqual(response[1]['ip_set'], params['ip_set'])

        #modify carrier
        new_params = {'name': 'hdsfgdsfg', 'ip_set': '192.168.1.124',
                      'carrier_id': carrier_id}
        response = self.client.modify_incoming_carrier(new_params)
        self.assertEqual(202, response[0])

        #check modified carrier details
        response = self.client.get_incoming_carrier({'carrier_id': carrier_id})
        self.assertEqual(response[1]['name'], new_params['name'])
        self.assertEqual(response[1]['ip_set'], new_params['ip_set'])

        #delete incoming carrier
        response = self.client.delete_incoming_carrier({'carrier_id':
                                                        carrier_id})
        self.assertEqual(204, response[0])

        #deleted carrier should not be available
        response = self.client.get_incoming_carrier({'carrier_id': carrier_id})
        self.assertEqual(404, response[0])
        self.assertTrue("error" in response[1])


class TestConference(PlivoTest):
    def test_get_all_conferences(self):
        response = self.client.get_live_conferences()
        valid_keys = ['conferences', 'api_id']
        self.check_status_and_keys(200, valid_keys, response)


class TestMessage(PlivoTest):
    def test_get_messages(self):
        response = self.client.get_messages()
        valid_keys = ['meta', 'objects', 'api_id']
        self.check_status_and_keys(200, valid_keys, response)

class TestCdr(PlivoTest):
    def test_get_all_cdrs(self):
        response = self.client.get_cdrs()
        valid_keys = ['meta', 'objects', 'api_id']
        self.check_status_and_keys(200, valid_keys, response)

class LiveCall(PlivoTest):
    def test_get_live_calls(self):
        response = self.client.get_live_calls()
        valid_keys = ['api_id', 'calls']
        self.check_status_and_keys(200, valid_keys, response)
        
	def test_send_and_get_message(self):
        params = {"src": DEFAULT_FROM_NUMBER, "dst": DEFAULT_TO_NUMBER,
                  "text": "Testing"}
        response = self.client.send_message(params)
        valid_keys = ["message", "message_uuid", "api_id"]
        self.check_status_and_keys(202, valid_keys, response)
        message_uuid = response[1]["message_uuid"][0]
        self.client.get_message({"record_id": message_uuid})
        
     


def get_client(AUTH_ID, AUTH_TOKEN):
    return plivo.RestAPI(AUTH_ID, AUTH_TOKEN)

if __name__ == "__main__":
    unittest.main()
