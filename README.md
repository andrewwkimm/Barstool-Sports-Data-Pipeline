# Barstool Sports Data Pipeline

## Introduction

I approached this assignment this assignment as if it were a case study where I was tasked to draw insights from the zip file with various data files provided to me, leading me to build developing this data pipeline project which enables me to do so.

On a high level, my pipeline does the following:

1) Extract data from Google Cloud Storage (where the contents of the zip files live), process it as an Arrow table, and upload it to BigQuery using PyArrow and GCP's Python SDKs.
2) Run a dbt project to deploy the data models I've written to BigQuery.
3) Render these processes as Prefect tasks and flows for orchestration.
4) Directly query from the final table(s) to power a Streamlit web app to track various metrics.

## Technologies

These are the main technologies used and why they were chosen. The majority of them were chosen because they are used at Barstool Sports based on our previous call and I wanted to get more exposure to them.

**Google Cloud Storage** - I originally wanted to use S3 but didn't largely due to convenience; I didn't want to go through the hassle of setting up billing for another cloud service and the two services are similar enough where they are interchangeable.

**BigQuery** - I recall this and Snowflake being used but Snowflake doesn't have a free tier.

**PyArrow** - I chose this over other popular tools such as pandas because it's lightweight, supports fast in-memory computation, is much more robust in processing parquet files if they ever become part of the pipeline.

**dbt** - Another tool mentioned that it is being used in Barstool's stack but is also useful here in managing SQL files.

**Streamlit** - This was mentioned as a potential tool to be used over Looker as the dashboard of choice so I decided to experiment this over other visualization tools.

## Miscellaneous

Here are some additional thoughts and/or extra context which I hope you find useful:

1) I found there are a lot of metrics that can be measured with just the three data files alone but for the sake of time, I decided to work on just one big data model which leverages all three, leading me the [user engagement table](dbt/models/marts/user_engagement_summary.sql). The metrics in the dashboard (i.e., views by content type, views by location, platform with highest engagement, etc.) are broad enough but still lead to insights with business value.
2) I noticed a disproportionately large number of null values as I got to visualizing the data. But I also saw that some columns with a high number of nulls like `content_type` can potentially be mapped to other columns like `content_barstoolContentID`. If this were a real project I'd bring up details like this to the data owner/product team and get more context to better help serve them.
3) There are endless amounts of considerations on the development side which I did not implement to be mindful of the time and taking into account how much I've already spent on this assignment alone. Some that pop up in my mind are:
    - **Tests**. I'd put in considerably more time into building up my test suite across the pipeline using pytest, dbt tests, etc.
    - **CI/CD**. Following up on the above, I'd think about improving the CI/CD pipeline as well. Thankfully, I already wrote a [general purpose template](https://github.com/andrewwkimm/modele) for Python project which has a basic CI/CD setup that I am using here.
    - **Containerization**. I've already done all my development in a DevContainer and feel that containerizing various parts of my pipeline wouldn't hurt for production environments.
    - **Large-scale data processing**. The bulk of the data processing is done in-memory with PyArrow but this becomes unsustainable with huge data sizes. Depending on how bigger the project gets, I'd first look into chunking to read data files in batches. For very large files, I'd start to explore other options.
4) For the resources I've used during this project, co-pilot was a huge help in speeding up development and writing up code for tools I am not as familar with, such as the Streamlit app. Beyond this, the official documentations for virtually every technology I've listed in the previous section were used and immensely helpful.
