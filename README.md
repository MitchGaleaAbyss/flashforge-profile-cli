# flashforge-profile-cli
To make management of slicer profiles simple and easy we have created abyss-flashforge repository. This repo stores the slicing profiles we use and provides a command line interface to make updating / modifying the profiles simple and scalable. 

## Profiles
Abyss Flashforge profiles are stored under profiles/

The naming is as follows : {machineID prefix}\_{nozzel diameter}\_{name}.cfg

## Installation
Run `cd <path/to/repo>/flashforge-profile-cli && sudo python3 setup.py install`

Note: flashforge-profile-cli can also be run without installation, by running `./flashforge-profile-cli` from repo directory

## Updating the flashforge profiles from the repo
The profiles are stored in the repo under profiles folder. We could open the Flashprint application and import each profile individually, but do we really want to do that?. For Flashprint to access the slicing profiles they must be in the Flashprint folder when opening the application to work. So we have created flashforge-profile-cli to help with this process. 

1. Run the following command, this will write all the the profiles that are located in flashforge-profile-cli to the flashprint profile directory and when you next open flashprint they will all be available to access.
```
flashforge-profile-cli update-profiles \
--repo-path <path/to/repo>/flashforge-profile-cli/profiles/
```

## Modifying Profiles
Say we have modified a setting on one of the profiles, for an example lets say we have changed our ABS filament supplier and the new filament prints better at 250 degrees rather than 240 degrees. If we wanted to change the temperature value for all profiles we would have to open each individually in the flashprint application, change the value and save the configuration, we don't want to do this. So here comes flashforge-profile-cli to the rescue again.

1. Open Flashprint and enter slice settings
2. We then edit the setting on a profile, in this example we will edit the Right Extruder Temperature on the profile abs-1.8-light. We will change the value from 240 to 250
3. Click the Save Configuration button
4. Close Flashprint 
5. We will run the following command to modify the Right Extruder Temperature parameter on all the other profiles. Firstly we cannot set the param without initially saving a input profile. This is because the values are not saved as readable values, for instance with the temperature it is saved as a weird byte value, this is what it appears as in the profile config file extruderTemp0=@Variant(\0\0\0\x87\x43p\0\0). At the moment we cannot decode these values so the best approach is to set the value in one config and then use the value that has been set in that config and set the other configs to match it. Also the param name will not directly match the name in the application, there is a mapping document in abyss-flashforge param-mappings.csv. Finally if we want the change to also be reflected in the repo, we can add the argument update-repo.
```
flashforge-profile-cli set-param \
 --param "extruderTemp0" \
 --input-profile-name "abs-1.8-light" \
 --repo-path <path/to/repo>/flashforge-profile-cli/profiles/ \
 --update-repo
```
6. All the profiles will have been updated, you can open up Flashprint now and check all the other profiles, the Right Extruder Temperature should be 250 for all profiles now 

Another use case would be where we only want to modify some of the profiles. For instance maybe we want to change the infill patterns on all the light profiles. We can use this using the search regex argument.

```
flashforge-profile-cli set-param \
 --param "fillPattern" \
 --input-profile-name "abs-1.8-light" \
 --search-regex "light"
 --repo-path <path/to/repo>/flashforge-profile-cli/profiles/ \
 --update-repo
```

## Updating Repo from profiles
There is also a command to update the repo from the flashforge profiles. 
```
flashforge-profile-cli update-repos \
--repo-path <path/to/repo>/flashforge-profile-cli/profiles/
```