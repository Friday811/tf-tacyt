### Tacyt PUP Identifier ###


#### Requirements ####
 - Python 2.7, Tacyt API isn't avaiable in 3.x
 - Install requirements from requirements.txt 
 - If using the default test script, create a models and pickles folder 
 - If using the default test script, set VERBOSE as desired and  RESET and TRAIN variables to True
 - If this is your first time running the script, comment out the model.load() line in the TRAIN section of the test script. You can uncomment it after creating an initial model.
 - You will need a [Tacyt](https://tacyt.elevenpaths.com) API key and invitation code.

#### API Keys ####
API keys should be put in a file called keys.api with format:
```
API_ID:KEY
SECRET:KEY
```

##### Test Data Set #####
The script was trained against a list of known safe apps taken from Google, Gameloft, and Facebook and a list of known malicious apps.
A list of malicious apps (available in maliciousapps/) was used to create the malicious application data.
A subset of good and malicious apps was removed and used to validate the model.

Multiple runs and validations average around a 75% detection rate of malicious applications.

##### Example Results #####
```
linux@ecs-tensorflow:~/tf-tacyt$ ./tft.py
Correctly identified malicious: 8/11
False positives: 2/89
linux@ecs-tensorflow:~/tf-tacyt$ ./tft.py
Correctly identified malicious: 8/11
False positives: 2/89
linux@ecs-tensorflow:~/tf-tacyt$ ./tft.py
Correctly identified malicious: 13/15
False positives: 3/85
linux@ecs-tensorflow:~/tf-tacyt$ ./tft.py
Correctly identified malicious: 7/9
False positives: 1/91
linux@ecs-tensorflow:~/tf-tacyt$ ./tft.py
Correctly identified malicious: 12/14
False positives: 4/86
linux@ecs-tensorflow:~/tf-tacyt$ ./tft.py
Correctly identified malicious: 10/12
False positives: 1/88
linux@ecs-tensorflow:~/tf-tacyt$ ./tft.py
Correctly identified malicious: 5/9
False positives: 2/91
```
