<div align="center">
  <a href="https://github.com/digital-external-env/envintegration">
    <img src="docs/images/main_logo.png" alt="Logo" width="60%" height="50%">
  </a>
</div>

## About

This library was created to develop solutions in the field of integrating the external environment of users into the ecosystem of their digital assistants. The library consists of several modules:
 * **pes_env** - for obtaining data on the psychoemotional state of the user from the physical environment
 * **pes_digenv** - for obtaining data on the psychoemotional state of the user from the digital environment
 * **env_manage** - for controlling the parameters of the external environment
 * **digital_hygiene** - for provide filtering of negative manifestations of the physical (projected) and digital external environment of users

## Built With

* [![Python][python-shield]][python-url]
* [![PDM][pdm-shield]][pdm-url]

## Requirements

* Python ~=3.10.6
* PDM ~=2.4.2 or pip ~=22.0

## Getting started

### Prerequisites

[**env_manage**] Before you start, you need to register your application with the [yandex authentication system](https://oauth.yandex.ru)
After that, using the received token, following the [instruction](https://yandex.ru/dev/id/doc/dg/oauth/concepts/about.html), you need to get the client_token to work with the API

[**pes_env**] Before you start, you also need to register your application with the [google o2 authentication system](https://developers.google.com/identity/protocols/oauth2?hl=en). After that, using the received token for `GoogleFitApi` using

### Installation

  ```sh
  pdm add git+ssh://github.com/digital-external-env/envintegration.git
  ```
  ```sh
  pip install git+ssh://github.com/digital-external-env/envintegration.git
  ````

## env_manage

This module contains methods for obtaining information about the smart home, smart home devices and managing these
devices. Modules methods allow you to separately manage smart home devices using the `YandexApi` class. The `YandexSession`/`YandexSessionAsync` class is used to control smart speakers. The library provides convenient direct access to device objects that allow you to access device-accessible methods

### Smart devices

You must create an instance of the Yandex API class by specifying in the client_token attribute a token received by
instructions

```python
from envintegration import YandexApi

api = YandexApi(client_token=client_token)
```

### Yandex smart speakers

You must create an instance of the YandexSession or YandexSessionAsync class by specifying the column id, obtained using
the above methods, as well as the login and password from the Yandex account.

```python
from yandex_smart_home_api.devices import YandexSession

my_station = YandexSession(login='', password='', station_id='')

```

In the future, examples will be discussed for the synchronous class YandexSession, all actions for asynchronous
YandexSessionAsync is similar except that these methods must be used asynchronously. In addition, the use of a session
is different when using an asynchronous class, so you must call the asynchronous authorization method before executing
methods:

```python
my_station.authorize()
```

All control of the column is carried out using scripts. You can obtain default and added scripts using the method:

```python
my_station.add_scenario(scenario_name='',
                        activation_command='',
                        instance='',
                        value='')
```

scenario_name - script name activation_command - voice command for script activation in Alice instance - takes the
values of:

'text _ action '- to perform the action specified in the value

'phrase _ action '- to voice the text specified in the value

value - action or phrase depending on the instance type

To update the script, use the method:

```python
my_station.update_scenario(scenario_id='',
                           scenario_name='',
                           activation_command='',
                           instance='',
                           value='')
```

To execute the script, use the method:

```python
my_station.exec_scenario(scenario_id='')
```

To delete a script, use the method:

```python
my_station.delete_scenario(scenario_id='')
```

## pes_env

This module contains methods for obtaining information about the user's activity with [Google Fit](https://developers.google.com/fit/rest/v1/get-started?hl=en):
- fitness bracelets
- smart watches
- sports applications

The methods allow you to get information about user activity through the Google FIT API. 
Data such as height and weight, number of steps, sleep and sleep phases, time intervals of activity.

You must create an instance of the GoogleFitApi class by specifying in the client_token attribute a token received by
instructions

```python
from api.py import GoogleFitApi

GFA = GoogleFitApi(token=client_token)
```

Note that all methods are asynchronous.
```python
from asyncio import get_event_loop
loop = get_event_loop()
```

## pes_digenv

This module is designed to determine the psychoemotional state of the user by exchanging text messages between people

```python
class TextEmotionApi:
    def is_toxic(self, text: str) -> bool:
        """
        Identifies toxicity in a text
        Args:
            texr (str): text

        Returns:
            bool: True if is toxic text, False otherwise

        """
        toxic = BertPredict()
        return bool(toxic.predict(text))

    def get_mat(self, text: str) -> tuple[int, int, list[Any]]:
        """
        Counting swear words
        Args:
            text: The text to be parsed is given as str. Can be any length

        Returns:
            tuple: Returns a tuple. The first cell of which contains the number of swear words,
                                    in the second - the percentage of swear words in the text
                                    and in the third - a lot of swear words.
        """
        return count_mat_detect(text)

    def emotion(self, text: str) -> dict[Any, Any]:
        """
        Identifies emotions in text

        Args:
            text (str): text

        Returns:
            dict: dict of emotions and their confidence
        """
        emo = Emotion()
        return emo.predict(text)
```
[in progress]

## digital_hygiene

[in progress]

## Documentation

[in progress]

## Examples

### env_manage

#### Getting Smart Home Information

```python
api.get_smart_home_info()
```

To simplify the operation, direct access to devices is implemented by creating an instance of the device class, and also
to methods available for devices, obtaining properties, abilities and information about the device.

(Note that all methods except set_id are asynchronous)

#### Getting device information and device management

```python
my_purifer = api.purifer.set_id(device_id='')
my_purifer.info()
my_purifer.on_off(value=True)

my_vacuum_cleaner = api.purifer.set_id(device_id='')
my_vacuum_cleaner.get_capabilities()
my_vacuum_cleaner.mode(value='turbo')

```

#### Create and execute scenario

```python
from asyncio import get_event_loop
loop = get_event_loop()

ys = YandexSessionAsync(login='login', password='password', station_id='3333333-0700-4e50-a82d-999d9999v9999')

loop.run_until_complete(ys.authorize())
loop.run_until_complete(ys.add_scenario(scenario_name='purifer',
                       activation_command='purifer',
                       instance='text_action',
                       value='выключи очиститель воздуха'))
scenarios = loop.run_until_complete(ys.get_scenarios())
scenario_id = [scenario['id'] for scenario in scenarios if scenario['name'] == 'purifer'][0]
loop.run_until_complete(ys.exec_scenario(scenario_id=scenario_id))
loop.run_until_complete(ys.delete_scenario(scenario_id=scenario_id))
```

### pes_env

#### Get the number of steps that the user takes on walks

```python
steps_from_walks = loop.run_until_complete(GoogleFitApi.get_steps_from_walks())
```

#### Get user weight records

```python
heights = loop.run_until_complete(GoogleFitApi.get_heights())
```

#### Get user height records

```python
weights = loop.run_until_complete(GoogleFitApi.get_weights())
```

#### Get records of the user's sleep and their sleep phase at a certain time

The time range for searching for sleep and sleep phases is given by two numbers. 
The start time is unixSleepStartTime. The end time is unixSleepEndTime.
The time must be specified in Unix epoch data format.
```python
sleeps_and_phases_by_time = loop.run_until_complete(GFA.get_sleeps_and_phases_by_time(unixSleepStartTime[1], unixSleepEndTime[1]))
```

### pes_digenv

[in progress]

### digital_hygiene

[in progress]

## Acknowledgments

<div align="center">
  <a href="https://github.com/digital-external-env/envintegration">
    <img src="docs/images/logo.png" alt="Logo" width="30%" height="30%">
    <img src="docs/images/img.png" alt="Logo" width="30%" height="30%">
  </a>
</div>

### Affiliation

The library was developed in: 
 - [ITMO University](https://itmo.ru)
 - [NCCR](https://actcognitive.org)

### Developers

 - Alina Remizova - analytic
 - Yuliya Khlyupina - analytic
 - Andrew Laptev - developer
 - Denis Kuznetsov - developer
 - Danila Korobkov - developer

### Contact

If you have any questions or comments on the project, email the developer - wvxp@mail.ru




<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[python-shield]: https://img.shields.io/badge/Python-%203.10-blue?style=for-the-badge&logo=python
[python-url]: https://www.python.org/downloads/release/python-310
[pdm-shield]: https://img.shields.io/badge/PDM-%202.4-purple?style=for-the-badge&logo=dpd
[pdm-url]: https://pdm.fming.dev/2.4
