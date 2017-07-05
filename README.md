### Tacyt PUP Identifier ###

#### Usage ####
See example.py script for usage.

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
linux@ecs-tensorflow:~/tf-tacyt$ ./example.py
Verbosity level set to:  -1
Correctly identified malicious: 24/32
False positives: 4/256
linux@ecs-tensorflow:~/tf-tacyt$ ./example.py
Verbosity level set to:  -1
Correctly identified malicious: 24/32
False positives: 2/256
linux@ecs-tensorflow:~/tf-tacyt$ ./example.py
Verbosity level set to:  -1
Correctly identified malicious: 28/36
False positives: 5/252
linux@ecs-tensorflow:~/tf-tacyt$ ./example.py
Verbosity level set to:  -1
Correctly identified malicious: 28/39
False positives: 5/249
linux@ecs-tensorflow:~/tf-tacyt$ ./example.py
Verbosity level set to:  -1
Correctly identified malicious: 30/37
False positives: 9/251
```

##### To-Do #####
 - Improve performance for vocab model
 - Improve separation between int/float and vocab graphs
 - Benchmark accuracy for vocab combined module
 - Fix saving/resuming for sentiment analyzer
 - Arbitrary application testing against model
 - Python package
