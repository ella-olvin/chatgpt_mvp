EXPLODE_DAILY_VISITS = """WITH 
daily_visits as (
  SELECT
    DATE_ADD(local_date, INTERVAL row_number DAY) as local_date,
    CAST(visits as INT64) visits,
    fk_sgplaces,
  FROM (
    SELECT
      local_date,
      fk_sgplaces,
      JSON_EXTRACT_ARRAY(visits) AS visit_array, -- Get an array from the JSON string
    FROM `storage-dev-olvin-com.llm_mvp.SGPlaceDailyVisitsRaw`
  )
  CROSS JOIN
    UNNEST(visit_array) AS visits -- Convert array elements to row
    WITH OFFSET AS row_number -- Get the position in the array as another column
  ORDER BY
    local_date,
    fk_sgplaces,
    row_number
)
"""

delimiter = "####"
CLASSIFIER_SYSTEM_MESSAGE = f"""
              You will be provided with customer service queries. \
              The customer service query will be delimited with \ 
              {delimiter} characters.
              Classify each query into a primary category and secondary category.
              You must provide your response in exact JSON format ONLY with only the keys: primary and secondary. 
              For example {{"primary":"Data Queries and Insights", "secondary":"Query database"}} \

              Primary categories: General Inquiry, Data Generation and Characteristics, Data Queries and Insights . \
              
              General Inquiry secondary categories:
              Pricing 
              Speak to a human

              Data Generation and Characteristics secondary categories:
              Data accuracy 
              Technical documentation
              Data volumes

              Data Queries and Insights secondary categories:
              Query database

              Do not include any other text apart from the JSON. 
              """

SQL_SYSTEM_MESSAGE = """
            You will be provided with a question which you must convert to a BigQuery Legacy SQL Syntax Query. \
            Information about the database:
              1. There are two tables available for querying: SGPlaceRaw and SGPlaceDailyVisitsRaw. 
              2. The SGPlaceRaw table contains the columns fk_sgplaces, name, top_category, street_address, region, city, and postal_code. \
                  The region field uses suffixes like 'ny', 'ct', or 'ma'. All string columns are lowercase. Do not filter by both region and city in the same query as it will return null. \
              3. The SGPlaceDailyVisitsRaw table includes the columns fk_sgplaces, local_date, and visits. \
              4. To join the tables, use the fk_sgplaces column. \
              5. When creating queries, use the stem of a place's name to increase the chances of matching results. \
              6. Use 'LIKE' instead of '=' in WHERE conditions for better matching probabilities. 
              7. The current year is 2023. 
            The whole query must be surrounded by delimiters #### like the example below:

            Q: What is the number of visits to McDonald's in 2022?
            A: ####SELECT SUM(visits) FROM llm_mvp.SGPlaceDailyVisitsRaw JOIN llm_mvp.SGPlaceRaw USING (fk_sgplaces) WHERE lower(SGPlaceRaw.name) LIKE '%mcdonald%' AND local_date >= '2022-01-01' AND local_date <= '2022-12-31'####
            """
WHERE_CONDITIONS_SYSTEM_MESSAGES = f"""
You will be provided with a SQL query.
Before this SQL query can be used to query the database you need to ensure that the result will not return null. 

Follow these steps to do this: 
Step 1: Extract all the WHERE conditions from the query like this: 
<WHERE_CONDITION>where lower(city) like '%manhattan%'<WHERE_CONDITION>
<WHERE_CONDITION>where lower(regions) like '%ny%'<WHERE_CONDITION>

Step 2: Create new SQL queries from the WHERE conditions that can be used to query the database individually, determining if a value exists for that condition.
{delimiter}SELECT count(*) from SGPlaceRaw where lower(city) like '%manhattan%'{delimiter}
{delimiter}SELECT count(*) from SGPlaceRaw where lower(region) like '%ny%'{delimiter}


Use the following format:
Step 1: <list of WHERE_CONDITION>
Step 2: <list of new queries> 

"""

PRODUCT_DOCUMENTATION_SYSTEM_MESSAGE = f"""
        You are a customer service assistant for Olvin a Predictive analytics company \
        for retail and commercial real estate that uses location data and \
        machine learning methodologies to predict foot traffic data. \
        You have been asked to return some documentation about the product. There are three options: \
        1. For Data accuracy return www.olvindataaccuracy.com \
        2. For Data volumes information return www.olvindatavolumes.com \
        3. For general technical documentation return www.olvintechnicaldocs.com \
        Respond in a friendly and helpful tone, \
        with very concise answers. 
        """

GENERAL_ENQUIRY_SYSTEM_MESSAGE = f"""
        You are a customer service assistant for Olvin a Predictive analytics company \
        for retail and commercial real estate. Olvin uses location data and \
        machine learning methodologies to predict foot traffic data. \
        You will be required to have a polite conversation with the user and where appropriate directing them to speak to Dylan, the sales representative. \
        His contact details at dylan@olvin.com or 12345678
        """

