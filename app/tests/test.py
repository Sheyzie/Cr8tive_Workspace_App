from configs import db_config
from .test_models import (
    TestClient, 
    TestPlan, 
    TestPayment,
    TestSubscription,
    TestVisit,
)


def main():
    TestClient.start_test()
    TestPlan.start_test()
    TestSubscription.start_test()
    TestPayment.start_test()
    TestVisit.start_test()

if __name__ == '__main__':
    main()

