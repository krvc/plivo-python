import unittest
import os
import random
import string

import plivo

try:
    from auth_secrets import AUTH_ID, AUTH_TOKEN
except ImportError:
    AUTH_ID, AUTH_TOKEN = os.getenv("AUTH_ID"), os.getenv("AUTH_TOKEN")
    if not (AUTH_ID and AUTH_TOKEN):
        raise Exception("Create a auth_secrets.py file or set AUTH_ID "
                        "and AUTH_TOKEN as environ values.")


class TestAccounts(unittest.TestCase):
    def setUp(self):
        auth_id = AUTH_ID
        auth_token = AUTH_TOKEN

        self.client = plivo.RestAPI(auth_id, auth_token)
        self.some_timezones = ['Pacific/Apia', 'Pacific/Midway']

    def test_get_account(self):
        response = self.client.get_account()
        self.assertEqual(200, response[0])
        valid_keys = ["account_type", "address", "auth_id", "auto_recharge",
                      "cash_credits", "city", "created", "enabled"]
        json_response = response[1]
        for key in valid_keys:
            self.assertTrue(key in json_response)

    def test_modify_account_name(self):
        random_name = "".join(random.sample('abcdef ghijkl', 10))
        params = {'name': random_name}
        self.client.modify_account(params)

        response = self.client.get_account()
        self.assertEqual(random_name, response[1]['name'])

    def test_modify_account_city(self):
        random_city = "".join(random.sample('abcdef ghijkl', 10))
        params = {'city': random_city}
        self.client.modify_account(params)

        response = self.client.get_account()
        self.assertEqual(random_city, response[1]['city'])

    def test_modify_account_address(self):
        random_address = "".join(random.sample('abcdef ghijklmnopqr 123456789', 20))
        params = {'address': random_address}
        self.client.modify_account(params)

        response = self.client.get_account()
        self.assertEqual(random_address, response[1]['address'])

    def test_modify_account_restricted_params(self):
        res = self.client.get_account()[1]
        
        random_name = "".join(random.sample('abcdef ghijkl', 10))
        random_city = "".join(random.sample('abcdef ghijkl', 10))
        random_address = "".join(random.sample('abcdef ghijklmnopqr 123456789', 20))
        random_state = "".join(random.sample('abcdefghijkl', 6))
        
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
        self.assertEqual(200, response[0])
        valid_keys = ["meta", "api_id", "objects"]
        json_response = response[1]
        for key in valid_keys:
            self.assertTrue(key in json_response)

    def test_subaccount_crud(self):
        random_letter = lambda: random.choice(string.ascii_letters)
        random_name = ''.join(random_letter() for i in range(8))
        response = self.client.create_subaccount(dict(name=random_name,
                                                 enabled=True))
        self.assertEqual(201, response[0])
        valid_keys = ["auth_id", "api_id", "auth_token"]
        json_response = response[1]
        for key in valid_keys:
            self.assertTrue(key in json_response)
        auth_id = json_response["auth_id"]
        response = self.client.get_subaccount(dict(subauth_id=auth_id))
        self.assertEqual(200, response[0])
        temp_name = "abcdef"
        self.client.modify_subaccount({'subauth_id': auth_id, 'name': temp_name,
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


class TestApplication(unittest.TestCase):
    def setUp(self):
        auth_id = AUTH_ID
        auth_token = AUTH_TOKEN
        self.client = plivo.RestAPI(auth_id, auth_token)

    def test_get_applications(self):
        response = self.client.get_applications()
        self.assertEqual(200, response[0])
        valid_keys = ["objects", "api_id", "meta"]
        json_response = response[1]
        for key in valid_keys:
            self.assertTrue(key in json_response)

    def test_applications_crud(self):
        params = {'answer_url': 'http://localhost.com', 'app_name': 'testappname'}
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


class TestEndpoint(unittest.TestCase):
    def setUp(self):
        auth_id = AUTH_ID
        auth_token = AUTH_TOKEN
        self.client = plivo.RestAPI(auth_id, auth_token)

    def test_get_endpoints(self):
        response = self.client.get_endpoints()
        self.assertEqual(200, response[0])
        valid_keys = ["objects", "api_id", "meta"]
        json_response = response[1]
        for key in valid_keys:
            self.assertTrue(key in json_response)

    
    def test_endpoint_crud(self):
        params = {'username': 'agdrasg', 'password': 'ahfdsgdf', 'alias': 'asasddas'}
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


class TestPricing(unittest.TestCase):
    def setUp(self):
        auth_id = AUTH_ID
        auth_token = AUTH_TOKEN
        self.client = plivo.RestAPI(auth_id, auth_token)

    def test_pricing(self):
        response = self.client.pricing({'country_iso': 'US'})
        self.assertEqual(200, response[0])
        valid_keys = ["country", "api_id", 'country_code', 'country_iso',
                      'phone_numbers', 'voice', 'message']
        json_response = response[1]
        for key in valid_keys:
            self.assertTrue(key in json_response)

    def test_invalid_country(self):
        response = self.client.pricing({'country_iso': 'USSDGF'})
        self.assertTrue("error" in response[1])

if __name__ == "__main__":
    unittest.main()
