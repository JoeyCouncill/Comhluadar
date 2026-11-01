## Description
<!-- Provide a brief description of the changes made. -->
Added starter Selenium tests for welcome, login, account creation and login-protected pages.
<br>*NOTE*: This suite is currently only for local machine testing. Additional set up and configuration is needed for running Selenium on an AWS EC2 instance.
## Testing procedures
<!-- Provide steps detailed enough for the team to understand how to test the change exists and works properly. -->
Make sure that you have the Selenium, pytest and pytest-django packages installed:
```shell
pip install selenium pytest pytest-django
```
You can either run the entire suite at once:
```python 
pytest selenium_tests.py
```
or run a certain class to focus on only the tests for a single page. The following command would only run tests in the TestWelcome class:
```python
pytest selenium_tests.py -k TestWelcome
```

As this version is only intended for local testing, make sure you also have the Google Chrome browser installed. While tests run and complete you will see browsers appear and close.
## PR Checklist
<!-- in addition to requiring one approval, the following checks must be completed successfully before merging. -->
- [ ] The project deploys and runs properly on a local environment.
- [ ] The project can be deployed to AWS and runs properly.
- [ ] Comprehensive unit tests for the change have been made in pytest(this may change/be removed).
- [ ] All pytest unit tests pass successfully.
- [ ] All Selenium tests pass successfully.
