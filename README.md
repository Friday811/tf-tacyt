### Tacyt PUP Identifier ###


#### Requirements ####
 - Python 2.7
 - Install requirements from requirements.txt 

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


The model successfully identified 8/10 malicious applications. There were 2 false positives.
Raw results are below.

###### Results ######
```
Test set #1
Malicious: 3.71596e-06/0.0
Safe: 0.999996/1.0
Test set #2
Malicious: 0.0811872/0.0
Safe: 0.918813/1.0
Test set #3
Malicious: 0.00522347/0.0
Safe: 0.994776/1.0
Test set #4
Malicious: 0.0/0.0
Safe: 1.0/1.0
Test set #5
Malicious: 0.718171/1.0
Safe: 0.281829/0.0
Test set #6
Malicious: 0.0704459/0.0
Safe: 0.929554/1.0
Test set #7
Malicious: 0.0753046/0.0
Safe: 0.924695/1.0
Test set #8
Malicious: 0.00860412/0.0
Safe: 0.991396/1.0
Test set #9
Malicious: 0.0268112/0.0
Safe: 0.973189/1.0
Test set #10
Malicious: 2.94245e-07/0.0
Safe: 1.0/1.0
Test set #11
Malicious: 0.0407652/0.0
Safe: 0.959235/1.0
Test set #12
Malicious: 0.00212446/0.0
Safe: 0.997876/1.0
Test set #13
Malicious: 0.0056729/0.0
Safe: 0.994327/1.0
Test set #14
Malicious: 0.0061801/0.0
Safe: 0.99382/1.0
Test set #15
Malicious: 0.00523235/0.0
Safe: 0.994768/1.0
Test set #16
Malicious: 0.00216547/0.0
Safe: 0.997835/1.0
Test set #17
Malicious: 0.115175/0.0
Safe: 0.884825/1.0
Test set #18
Malicious: 0.0/0.0
Safe: 1.0/1.0
Test set #19
Malicious: 0.0431763/0.0
Safe: 0.956824/1.0
Test set #20
Malicious: 0.0432797/0.0
Safe: 0.95672/1.0
Test set #21
Malicious: 0.045642/0.0
Safe: 0.954358/1.0
Test set #22
Malicious: 2.34047e-08/0.0
Safe: 1.0/1.0
Test set #23
Malicious: 2.77009e-10/0.0
Safe: 1.0/1.0
Test set #24
Malicious: 0.0/0.0
Safe: 1.0/1.0
Test set #25
Malicious: 0.0/0.0
Safe: 1.0/1.0
Test set #26
Malicious: 8.86219e-14/0.0
Safe: 1.0/1.0
Test set #27
Malicious: 0.00507688/0.0
Safe: 0.994923/1.0
Test set #28
Malicious: 0.00969869/0.0
Safe: 0.990301/1.0
Test set #29
Malicious: 0.0/0.0
Safe: 1.0/1.0
Test set #30
Malicious: 0.00645118/0.0
Safe: 0.993549/1.0
Test set #31
Malicious: 5.58243e-08/0.0
Safe: 1.0/1.0
Test set #32
Malicious: 0.0350028/1.0
Safe: 0.964997/0.0
Test set #33
Malicious: 0.0320817/0.0
Safe: 0.967918/1.0
Test set #34
Malicious: 2.77165e-26/0.0
Safe: 1.0/1.0
Test set #35
Malicious: 0.138874/0.0
Safe: 0.861126/1.0
Test set #36
Malicious: 0.0220281/0.0
Safe: 0.977972/1.0
Test set #37
Malicious: 6.6841e-29/0.0
Safe: 1.0/1.0
Test set #38
Malicious: 0.941654/1.0
Safe: 0.0583459/0.0
Test set #39
Malicious: 0.00491712/0.0
Safe: 0.995083/1.0
Test set #40
Malicious: 0.00254283/1.0
Safe: 0.997457/0.0
Test set #41
Malicious: 0.0309613/0.0
Safe: 0.969039/1.0
Test set #42
Malicious: 0.0/0.0
Safe: 1.0/1.0
Test set #43
Malicious: 7.2654e-06/0.0
Safe: 0.999993/1.0
Test set #44
Malicious: 1.21794e-10/0.0
Safe: 1.0/1.0
Test set #45
Malicious: 0.024183/0.0
Safe: 0.975817/1.0
Test set #46
Malicious: 0.0/0.0
Safe: 1.0/1.0
Test set #47
Malicious: 1.43149e-35/0.0
Safe: 1.0/1.0
Test set #48
Malicious: 2.77701e-05/0.0
Safe: 0.999972/1.0
Test set #49
Malicious: 0.0919739/0.0
Safe: 0.908026/1.0
Test set #50
Malicious: 0.107843/0.0
Safe: 0.892157/1.0
Test set #51
Malicious: 3.23452e-34/0.0
Safe: 1.0/1.0
Test set #52
Malicious: 0.00595645/0.0
Safe: 0.994044/1.0
Test set #53
Malicious: 1.85911e-07/0.0
Safe: 1.0/1.0
Test set #54
Malicious: 0.025921/0.0
Safe: 0.974079/1.0
Test set #55
Malicious: 0.0020945/0.0
Safe: 0.997905/1.0
Test set #56
Malicious: 3.42515e-10/0.0
Safe: 1.0/1.0
Test set #57
Malicious: 0.00541206/0.0
Safe: 0.994588/1.0
Test set #58
Malicious: 0.00564376/0.0
Safe: 0.994356/1.0
Test set #59
Malicious: 0.0342731/0.0
Safe: 0.965727/1.0
Test set #60
Malicious: 3.01935e-25/0.0
Safe: 1.0/1.0
Test set #61
Malicious: 0.390817/0.0
Safe: 0.609183/1.0
Test set #62
Malicious: 0.372167/0.0
Safe: 0.627833/1.0
Test set #63
Malicious: 0.0337618/0.0
Safe: 0.966238/1.0
Test set #64
Malicious: 0.592058/1.0
Safe: 0.407942/0.0
Test set #65
Malicious: 0.00567781/0.0
Safe: 0.994322/1.0
Test set #66
Malicious: 0.0438569/0.0
Safe: 0.956143/1.0
Test set #67
Malicious: 0.0300688/0.0
Safe: 0.969931/1.0
Test set #68
Malicious: 0.998971/1.0
Safe: 0.00102922/0.0
Test set #69
Malicious: 0.0108883/0.0
Safe: 0.989112/1.0
Test set #70
Malicious: 0.00711731/0.0
Safe: 0.992883/1.0
Test set #71
Malicious: 0.249077/0.0
Safe: 0.750923/1.0
Test set #72
Malicious: 0.0275731/0.0
Safe: 0.972427/1.0
Test set #73
Malicious: 0.00507687/0.0
Safe: 0.994923/1.0
Test set #74
Malicious: 0.00627009/0.0
Safe: 0.99373/1.0
Test set #75
Malicious: 0.999919/1.0
Safe: 8.13238e-05/0.0
Test set #76
Malicious: 0.252906/0.0
Safe: 0.747093/1.0
Test set #77
Malicious: 0.00507688/0.0
Safe: 0.994923/1.0
Test set #78
Malicious: 0.831686/1.0
Safe: 0.168314/0.0
Test set #79
Malicious: 0.0/0.0
Safe: 1.0/1.0
Test set #80
Malicious: 0.0/0.0
Safe: 1.0/1.0
Test set #81
Malicious: 1.02413e-31/0.0
Safe: 1.0/1.0
Test set #82
Malicious: 0.00605242/0.0
Safe: 0.993948/1.0
Test set #83
Malicious: 0.0227455/0.0
Safe: 0.977255/1.0
Test set #84
Malicious: 0.0066482/0.0
Safe: 0.993352/1.0
Test set #85
Malicious: 0.0178748/0.0
Safe: 0.982125/1.0
Test set #86
Malicious: 4.16021e-21/0.0
Safe: 1.0/1.0
Test set #87
Malicious: 9.11534e-09/0.0
Safe: 1.0/1.0
Test set #88
Malicious: 6.788e-06/0.0
Safe: 0.999993/1.0
Test set #89
Malicious: 0.0800788/0.0
Safe: 0.919921/1.0
Test set #90
Malicious: 0.978275/0.0
Safe: 0.0217251/1.0
Test set #91
Malicious: 0.00793832/0.0
Safe: 0.992062/1.0
Test set #92
Malicious: 0.992127/1.0
Safe: 0.00787282/0.0
Test set #93
Malicious: 0.0254099/0.0
Safe: 0.97459/1.0
Test set #94
Malicious: 0.00342598/0.0
Safe: 0.996574/1.0
Test set #95
Malicious: 5.20546e-05/0.0
Safe: 0.999948/1.0
Test set #96
Malicious: 0.00614737/0.0
Safe: 0.993853/1.0
Test set #97
Malicious: 0.51/0.0
Safe: 0.49/1.0
Test set #98
Malicious: 8.62067e-09/0.0
Safe: 1.0/1.0
Test set #99
Malicious: 0.0/0.0
Safe: 1.0/1.0
Test set #100
Malicious: 0.0235699/0.0
Safe: 0.97643/1.0
```
