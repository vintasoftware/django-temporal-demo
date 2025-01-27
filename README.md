# Django and Temporal Demo

This is a sample project to demo the usage of Temporal in a Django project for managing background and scheduled jobs.

## Features

The project implements a health activity tracking system with generation of a monthly calories burnt report.

The report generation is triggered in day 5 of every month but it can also be triggered manually through Django admin.

After generating each report the application sends an email to the user with their result.

After processing all calories reports and sending them to the users, the workflow sends an email to the admin saying the processed has completed successfully.


## Implementation Details

* The Temporal workers was defined as a custom Django management command to ensure Django ORM is instantiated and available on Temporal activities.
* We're using the sync version of the ORM methods, so this setup should also work in older versions of Django.
* We have a Docker setup to make this easier to test. To run all the container you just need to use `docker compose up -d`. The Django local web server will be available through `http://localhost:8000` and the temporal web service is available through `http://localhost:8088`. We also included a few other tools in this setup to make the app more interesting:
    * PostgreSQL as a database for Django and the Workers
    * Mailpit as a mock to an SMTP server


## Commercial Support

[![alt text](https://avatars2.githubusercontent.com/u/5529080?s=80&v=4 "Vinta Logo")](https://www.vintasoftware.com/)

This is an open-source project maintained by [Vinta Software](https://www.vinta.com.br/). We are always looking for exciting work! If you need any commercial support, feel free to get in touch: contact@vinta.com.br