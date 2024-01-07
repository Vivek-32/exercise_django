INSERT_ONE_DATA = {
    "country": {
        "name": "India",
        "country_code": "IN",
        "curr_symbol": "₹",
        "phone_code": "+91"
    },
    "state": {
        "name": "Odisha",
        "state_code": "OD",
        "gst_code": "GSTINOD123"
    },
    "city": {
        "name": "Cuttuck",
        "city_code": "CTC",
        "phone_code": "+91",
        "population": 25320000,
        "avg_age": 37.0,
        "num_of_adult_males": 220000,
        "num_of_adult_females": 128000
    }
}

INSERT_MANY_DATA = {
    "country": [
        {
            "name": "Canada",
            "country_code": "CA",
            "curr_symbol": "$",
            "phone_code": "+1"
        },
        {
            "name": "USA",
            "country_code": "US",
            "curr_symbol": "$",
            "phone_code": "+1"
        }
    ],
    "state": [
        {
            "name": "Ontario",
            "state_code": "ON",
            "gst_code": "GSTCAON123",
            "country_code": 'CA'
        },
        {
            "name": "California",
            "state_code": "CA",
            "gst_code": "GSTUSCA123",
            "country_code": 'US'            
        },
    ],
    "city": [
        {
        "name": "Toronto",
        "city_code": "TOR",
        "phone_code": "+1",
        "population": 350000,
        "avg_age": 35.0,
        "num_of_adult_males": 30000,
        "num_of_adult_females": 28000,
        "state_code": "ON"
    },
    {
        "name": "Los Angeles",
        "city_code": "LA",
        "phone_code": "+1",
        "population": 2350000,
        "avg_age": 30.0,
        "num_of_adult_males": 220000,
        "num_of_adult_females": 128000,
        "state_code": "CA"
    }
    ]
}