from configs import db_config, app_config
from helpers.db_helpers import delete_db
from .test_models import (
    TestClient, 
    TestPlan, 
    TestPayment,
    TestSubscription,
    TestVisit,
    DB_NAME
)

import os

os.environ.setdefault('CURRENT_WORKING_DB_ENVIRON', 'test')


def main(**kwargs):
    arguments = {}
    if kwargs:
        arguments = kwargs.get('validated_args', {})
    
    model = arguments.get('model', [])
    try:
        if len(model) == 0:
            TestClient.start_test()
            delete_db(app_config.BASE_DIR, DB_NAME)
            TestPlan.start_test()
            delete_db(app_config.BASE_DIR, DB_NAME)
            TestSubscription.start_test()
            delete_db(app_config.BASE_DIR, DB_NAME)
            TestPayment.start_test()
            delete_db(app_config.BASE_DIR, DB_NAME)
            TestVisit.start_test()
        else:
            match model[0]:
                case 'client':
                    TestClient.start_test()
                case 'plan':
                    TestPlan.start_test()
                case 'subscription':
                    TestSubscription.start_test()
                case 'payment':
                    TestPayment.start_test()
                case 'visit':
                    TestVisit.start_test()
                case _:
                    print('Unknown argument provided for test.')

        # clean up
        delete_db(app_config.BASE_DIR, DB_NAME)
    except Exception as err:
        # clean up
        delete_db(app_config.BASE_DIR, DB_NAME)
        raise err

if __name__ == '__main__':
    main()

