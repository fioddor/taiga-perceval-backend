# Testing
This doc is about testing Perceval's backend for Taiga API.

## Organization
Using unittest's terminology, **test_taiga.py** has its tests organized in following TestCases:
- TestTaigaCommand
- TestTaigaBackend
- TestTaigaClientAgainstRealServer (this one is disabled by default)
- TestTaigaClientAgainstMockServer
- TestsUnderConstruction (disabled draft testcases)
- Utilities (disabled by default)

## Basic regression Testing
As its name states, _TestTaigaClientAgainstMockServer_ mocks the Taiga server. As stated in Perceval's [README.md](https://github.com/chaoss/grimoirelab-perceval) we use _httpretty_ for that, and expect it to be preinstalled. If you have pip installed (docker image grimoirelab/full has it) you can install httpretty with

`$ sudo pip install httpretty`

You should get something like this:

> Collecting httpretty
>   Downloading https://files.pythonhosted.org/packages/24/30/7eb83a91269cd4136d35f62d27a199c916bbf8a2ccb1c74f9322148216cf/httpretty-1.0.2.tar.gz (399kB)
>      |████████████████████████████████| 399kB 3.6MB/s 
> Building wheels for collected packages: httpretty
>   Building wheel for httpretty (setup.py) ... done
>   Created wheel for httpretty: filename=httpretty-1.0.2-cp35-none-any.whl size=26458 sha256=6bacdb422233ebfeecbe484a9ec7aa3e0cfaa5bff6b09a1c93482d2214f3d792
>   Stored in directory: /root/.cache/pip/wheels/43/b3/cd/38dad43e9a47119274e56dd1574be05973bd6020e79f0846d3
> Successfully built httpretty
> Installing collected packages: httpretty
> Successfully installed httpretty-1.0.2
> WARNING: You are using pip version 19.3.1; however, version 20.1.1 is available.
> You should consider upgrading via the 'pip install --upgrade pip' command.

To run all enabled tests: `$ ./test_taiga.py`

As it is configured in 2020-07-08, this will run 41 tests in scant seconds and report OK with 14 skipped tests:

> Debug: Executing test_taiga as __main__ (called as ./script.py or as python3 script.py).
> \----------------------------------------
> Testing Taiga v0.11.0-20200625A
> test_categories (__main__.TestTaigaBackend)
> No exception raised when accessing that member. ... 
> ./test_taiga.py:224: DeprecationWarning: Please use assertEqual instead.
>   self.assertEquals( 7 , len(Taiga.CATEGORIES) )
> ok
> test_classified_fields (__main__.TestTaigaBackend)
> No exception raised on accessing that member. ... 
> ok
> test_fetch_items (__main__.TestTaigaBackend)
> Fech_items response contains expected items. ... 
> INFO:perceval.backends.core.taiga:TaigaMinClient-20200621A.rp_pages got yet 60 items out of 81.
> INFO:perceval.backends.core.taiga:TaigaMinClient-20200621A.rp_pages got yet 81 items out of 81.
> ok
> test_has_archiving (__main__.TestTaigaBackend)
> Expect False, for the moment. ... 
> ok
> test_has_resuming (__main__.TestTaigaBackend)
> Expect False, for the moment. ... 
> ok
> test_init_missing_arguments (__main__.TestTaigaBackend)
> Calling init with missing expected arguments is wrong and raises exceptions. ... 
> ok
> test_metadata_category (__main__.TestTaigaBackend)
> Each item category is identified. ... 
> INFO:perceval.backends.core.taiga:TaigaMinClient-20200621A.rp_pages got yet 60 items out of 81.
> INFO:perceval.backends.core.taiga:TaigaMinClient-20200621A.rp_pages got yet 81 items out of 81.
> ok
> test_tag (__main__.TestTaigaBackend)
> Feched items will and can be tagged. ... 
> ok
> test_init_with_token (__main__.TestTaigaClientAgainstMockServer)
> A token-born client... ... 
> ok
> test_init_with_user_and_pswd (__main__.TestTaigaClientAgainstMockServer)
> A client is created without token. ... 
> ok
> test_init_without_expected_arguments_causes_exception (__main__.TestTaigaClientAgainstMockServer)
> Raises exception if client is requested without expected arguments. ... 
> ok
> test_initialization (__main__.TestTaigaClientAgainstMockServer)
> Taiga Client initializations. ... 
> ok
> test_login_fail (__main__.TestTaigaClientAgainstMockServer)
> Taiga denies permission. ... 
> ERROR:perceval.backends.core.taiga:TaigaMinClient-20200621A.login failed:
> ERROR:perceval.backends.core.taiga:TaigaMinClient-20200621A.login Rq.headers : {'Connection': 'close', 'User-Agent': 'python-requests/2.21.0', 'Content-Type': 'application/json', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Content-Length': '64'}
> ERROR:perceval.backends.core.taiga:TaigaMinClient-20200621A.login Rq.body : bytearray(b'{ "type": "normal", "username": "a_user", "password": "a...d" }')
> ERROR:perceval.backends.core.taiga:TaigaMinClient-20200621A.login Rs.status_code : 401
> ERROR:perceval.backends.core.taiga:TaigaMinClient-20200621A.login Rs.text:
> { "etc":"etc" }
> ok
> test_no_permission (__main__.TestTaigaClientAgainstMockServer)
> Taiga denies permission. ... 
> ok
> test_pj_epics (__main__.TestTaigaClientAgainstMockServer)
> Taiga Project Epics. ... 
> INFO:perceval.backends.core.taiga:TaigaMinClient-20200621A.rp_pages got yet 37 items out of 37.
> ok
> test_pj_issues_stats (__main__.TestTaigaClientAgainstMockServer)
> proj_issues_stats retrieves the expected elements. ... 
> ok
> test_pj_stats (__main__.TestTaigaClientAgainstMockServer)
> proj_stats retrieves the expected elements. ... 
> ok
> test_pj_tasks (__main__.TestTaigaClientAgainstMockServer)
> Taiga Project Tasks. ... 
> INFO:perceval.backends.core.taiga:TaigaMinClient-20200621A.rp_pages got yet 38 items out of 38.
> ok
> test_pj_userstories (__main__.TestTaigaClientAgainstMockServer)
> Taiga Project User Stories. ... 
> INFO:perceval.backends.core.taiga:TaigaMinClient-20200621A.rp_pages got yet 38 items out of 38.
> ok
> test_pj_wiki_pages (__main__.TestTaigaClientAgainstMockServer)
> Taiga Project Wiki Pages. ... 
> INFO:perceval.backends.core.taiga:TaigaMinClient-20200621A.rp_pages got yet 36 items out of 36.
> ok
> test_proj (__main__.TestTaigaClientAgainstMockServer)
> Taiga Project data. ... 
> INFO:perceval.backends.core.taiga:TaigaMinClient-20200621A.rp_pages got yet 60 items out of 81.
> INFO:perceval.backends.core.taiga:TaigaMinClient-20200621A.rp_pages got yet 81 items out of 81.
> INFO:perceval.backends.core.taiga:TaigaMinClient-20200621A.rp_pages got yet 38 items out of 38.
> ok
> test_rq_max (__main__.TestTaigaClientAgainstMockServer)
> Rq stops paginating on user limit. ... 
> INFO:perceval.backends.core.taiga:TaigaMinClient-20200621A.rp_pages got yet 60 items out of 81.
> INFO:perceval.backends.core.taiga:TaigaMinClient-20200621A.rp_pages got yet 60 items out of 81.
> INFO:perceval.backends.core.taiga:TaigaMinClient-20200621A.rp_pages got yet 81 items out of 81.
> INFO:perceval.backends.core.taiga:TaigaMinClient-20200621A.rp_pages got yet 60 items out of 81.
> INFO:perceval.backends.core.taiga:TaigaMinClient-20200621A.rp_pages got yet 81 items out of 81.
> ok
> test_throttling (__main__.TestTaigaClientAgainstMockServer)
> Taiga blocks reporting throttling. ... 
> INFO:perceval.backends.core.taiga:Sleeping for 2 seconds...
> ok
> test_wrong_token (__main__.TestTaigaClientAgainstMockServer)
> Taiga rejects wrong token. ... 
> ok
> test_init_with_user_and_pswd (__main__.TestTaigaClientAgainstRealServer)
> A pswd-born client is created without token. ... skipped 'Tests against real server disabled by default to avoid annoying the real taiga service.'
> test_initialization (__main__.TestTaigaClientAgainstRealServer)
> Test Taiga Client initializations. ... skipped 'Tests against real server disabled by default to avoid annoying the real taiga service.'
> test_pj_epics (__main__.TestTaigaClientAgainstRealServer)
> Taiga Project Epics. ... skipped 'Tests against real server disabled by default to avoid annoying the real taiga service.'
> test_pj_issues_stats (__main__.TestTaigaClientAgainstRealServer)
> Taiga Project Issues Stats ... skipped 'Tests against real server disabled by default to avoid annoying the real taiga service.'
> test_pj_stats (__main__.TestTaigaClientAgainstRealServer)
> Taiga Project Stats ... skipped 'Tests against real server disabled by default to avoid annoying the real taiga service.'
> test_pj_tasks (__main__.TestTaigaClientAgainstRealServer)
> Taiga Project Tasks. ... skipped 'Tests against real server disabled by default to avoid annoying the real taiga service.'
> test_pj_userstories (__main__.TestTaigaClientAgainstRealServer)
> Taiga Project User Stories. ... skipped 'Tests against real server disabled by default to avoid annoying the real taiga service.'
> test_pj_wiki_pages (__main__.TestTaigaClientAgainstRealServer)
> Taiga Project Wiki Pages. ... skipped 'Tests against real server disabled by default to avoid annoying the real taiga service.'
> test_proj (__main__.TestTaigaClientAgainstRealServer)
> Taiga Project data. ... skipped 'Tests against real server disabled by default to avoid annoying the real taiga service.'
> test_proj_export (__main__.TestTaigaClientAgainstRealServer)
> Taiga export doesn't work due to permissions. ... skipped 'Tests against real server disabled by default to avoid annoying the real taiga service.'
> test_wrong_token (__main__.TestTaigaClientAgainstRealServer)
> Taiga rejects wrong tokens. ... skipped 'Tests against real server disabled by default to avoid annoying the real taiga service.'
> test_backend_class (__main__.TestTaigaCommand)
> It's backend is the expected one. ... ok
> test_setup_cmd_parser (__main__.TestTaigaCommand)
> The parser object is correctly initialized. ... ok
> test_api_command (__main__.TestsUnderConstruction) ... skipped 'This case is a draft or under construction.'
> test_under_construction (__main__.TestsUnderConstruction)
> This test is under construction. ... skipped 'This case is a draft or under construction.'
> test_capture (__main__.Utilities)
> Runner for testing utilities. ... skipped 'This utility runner is disabled by default'
> test_http_codes (__main__.Utilities) ... ok
> 
> ----------------------------------------------------------------------
> Ran 41 tests in 2.435s
> 
> OK (skipped=14)


## Unit testing and test development

### Running isolated TestCases
While developing it is a good practice to separate the stable tests from the ones being developed, so there's a TestCase named _TestsUnderConstruction_ for that. You can run that TestCase alone as follows:

`$ ./test_taiga.py TestsUnderConstruction`

### Utilities
You'll probably want to mock other API responses. Among the _Utilities_ class _test_capture_, in combination with _capture_*_ methods helps you to capture series of responses (Taiga API returns paginated results).
This class isn't really meant as a pure TestCase but as a collector of utilities. However, it contains tests for these utilities, so it indeed plays the TestCase role.


## Full regression Testing
All tests against a real server are skipped by default  to avoid annoying the real Taiga service. In order to run them you need to comment out the _@unittest.skip_ decorator in line 249 and get a valid API token for your Taiga instance and edit the **test_taiga.cfg** file to feed it at the _Token_ entry (at line 11).

```
# Testing data
# 

[taiga-site]
API_URL = https://api.taiga.io/api/v1/

[taiga-default-credentials]
User     = ledamc-izubiaurre
Password = xxxcensoredxxx

Token    = xxxcensoredxxx

[test-data]
```

The tests against a real server are configured to call [Taiga,io](https://taiga.io) service. If you have an own Taiga instance you also need to adapt the _API_URL_ entry (at line 5) accordingly.

And there's at least two tests that get a token from Taiga's API with a set of valid credentials. If you want to run them, you also need to adapt the _User_ and _Password_ entries a (at lines 8 and 9) to feed the valid credentials.


Specific test data and expected results are provided in the same **test_taiga.cfg** file. They might have become obsolete since they were captured and you use them again. You should re-baseline them in your first runs.



