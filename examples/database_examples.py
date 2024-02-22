datbase_examples: {
    "query_example_1": [
        {
        "op": ">",
        "field": "time",
        "value": "2023-08-01T00:00:00.000000"
        },
        {
        "op": "<",
        "field": "time",
        "value": "2023-08-01T02:00:00.000000"
        }
    ],
    "query_example_2": [
        {
        "op": ">",
        "field": "time",
        "value": "2023-08-01T00:00:00.000000"
        },
        {
        "op": "<",
        "field": "time",
        "value": "2023-08-15T00:00:00.000000"
        },
        {
        "op": "=",
        "field": "source",
        "value": "local_db"
        },
    ]
}