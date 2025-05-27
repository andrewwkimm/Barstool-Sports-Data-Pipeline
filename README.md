# Barstool Sports Data Pipeline

## Introduction

I decided to work on this assignment as if it were a case study where I was tasked to draw insights from the zip file with various data files provided to me, leading me to build developing this data pipeline project which enables me to do so.

Not every decision I've made in this project is practical and there are many additional considerations which I'll go over.

On a high level, my pipeline does the following:

1) Extract data from Google Cloud Storage (where the contents of the zip files live), process it as an Arrow table, and upload it to BigQuery using PyArrow and GCP's Python SDKs.
2) Run a dbt project to deploy the data models I've written to BigQuery.
3) Render these processes as Prefect tasks and flows for orchestration.
4) Directly query from the final table(s) to power a Streamlit web app to track various metrics.

## Technologies

These are the main technologies used and why they were chosen. The majority of them were picked because they are used at Barstool Sports based on our previous call and I wanted to get more exposure to them.

**Google Cloud Storage** - I originally wanted to use S3 but didn't largely due to convenience; I didn't want to go through the hassle of setting up billing for another cloud service and the two services are similar enough where they are interchangeable.

**BigQuery** - I recall this and Snowflake being used but Snowflake doesn't have a free tier.

**PyArrow** - I chose this over other popular tools such as pandas because it's lightweight, supports fast in-memory computation, is much more robust in processing parquet files if they ever become part of the pipeline.

**dbt** - Another tool directly mentioned that it is being used in Barstool's stack but is also useful here in managing SQL files.

**Streamlit** - This was mentioned as a potential tool to be used over Looker as the dashboard of choice so I decided to experiment this over other visualization tools.
