# ansible-hiera

## Setup (follow before Quick Use)

### Installation

    brew install python
    brew install ansible

Ensure you are using the python from brew

    $ which python
    /usr/local/bin/python

### Ansible Configuration

**IF** running on Hiera hosts (i.e. using your own information, or using the dynamic inventory host file in this repo), **relies** on a few things being set in your ansible.cfg:
* Comment out line: ask_pass = True
* Uncomment line: host_key_checking = False
* Uncomment line: remote_user = <user> (set to xdeploy)
* Uncomment line: private_key_file = <file> (set to xdeploy private key on local machine running Ansible)

> If you're not comfortable changing your Ansible remote user and private_key_file to this, use all Ansible commands with:
>    -u xdeploy --private-key="path/to/key"

### Cloning

Clone this repository.
Clone the mopsCompassHiera repository if you do not already have it. Create a symlink to the mopsCompassHiera repository (**if you don't have one already**):
> Please change the first path to the path to your mopsCompassHiera repository

    sudo ln -s /current/location/of/mopsCompassHiera/ /etc/hiera

## Quick Usage

    cd ansible-hiera

#### Lookup
Run a lookup locally:

    ansible localhost -i hosts -c local -m hieraMod --args="option=lookup hieraFile=/etc/hiera/merlin-hiera.yaml service=entityDataService env=cmpstkMerlinIngest key=xmx,ds_properties" -v

You should get back a dictionary of the values for the keys xmx and ds_properties for the above service/environment combination.

#### View All
Run a view all locally:

    ansible localhost -i hosts -c local -m hieraMod --args="option=viewAll hieraFile=/etc/hiera/merlin-hiera.yaml service=entityDataService env=cmpstkMerlinIngest key=ds_vars resolve=False" -v

You should get back a multi-level description of the values for the ds_vars key on each Hiera level.

#### Config File
Create a config file:

> Username and Password below are your credentials into the Compass Gerrit Git Repo (where mopsCompassHiera repo is located, they are your NT credentials).
More info on the [wiki](http://teamcompass.cable.comcast.com/display/bitt/RB+Gerrit).

    ansible localhost -i hosts -c local -m hieraMod --args="option=configFile hieraFile=/etc/hiera/merlin-hiera.yaml service=entityDataService env=cmpstkMerlinIngest user=### pass=###" -v


You should now have a file in your /tmp directory called DS_Configuration.properties

## Adding Module to Playbook
Copy the library folder in this repository to the folder where your playbook is (this contains the module)

#### Lookup
Lookup example:

```
    - name: Lookup
      connection: local
      hieraMod: option=lookup hieraFile=/etc/hiera/merlin-hiera.yaml service=entityDataService env=cmpstkMerlinIngest key="alive.check.force.up"
```

#### View All
View All example:

```
    - name: ViewAll
      connection: local
      hieraMod: option=viewAll hieraFile=/etc/hiera/merlin-hiera.yaml service=entityDataService env=cmpstkMerlinIngest key="ds_vars" resolve=True
```

#### Config File
Either of these methods will need to be followed by the [copy module](http://docs.ansible.com/ansible/copy_module.html) in order to move the file created to the correct host

Config File example #1:
```
    vars_prompt:
    - name: gitUser
      prompt: Comcast GitHub Username
      private: no
    - name: gitPass
      prompt: Comcast GitHub Password
      private: yes

    - name: ConfigFile
      connection: local
      hieraMod: option=configFile hieraFile=/etc/hiera/merlin-hiera.yaml service=entityDataService env=cmpstkMerlinIngest user="{{gitUser}}" pass="{{gitPass}} key=xmx,ds_properties"
```

Config File example #2:
```
    - name: ConfigFile
      connection: local
      hieraMod: option=configFile hieraFile=/etc/hiera/merlin-hiera.yaml service=entityDataService env=cmpstkMerlinIngest file="path/to/test.properties"
```

## Module Capabilities
Module is able to key lookups, full lookups, and create svc/env config files.
This hierarchy makes use of the service, environment, and host variables for its filing.
**It is assumed** you know the appropriate combination (i.e., whether your combo needs a host variable).
If you do not include this information when needed, key lookups can fail or simply be incorrect, and config files may have blanks or incorrect information.

Options are:
* lookup
    * Required additional arguments:
        * service
        * environment
    * Optional additional arguments:
        * host
        * key
            * Key(s) to find value of, based on hierarchy
                * Comma separated for multiple lookups
            * If not passed, module will grab all relevant keys for given env/svc
* viewAll
    * Required additional arguments:
        * service
        * environment
        * key
            * Key(s) to find value of on all hierarchy levels
                * Comma separated for multiple lookups
            * If not passed, module will grab all relevant keys for given env/svc
        * resolve
            * Indicates whether values containing Hiera variables (designated by this structure: %{hiera('keyToReplace')} ) should be resolved (filled in) or not
    * Optional additional arguments:
        * host
* configFile
    * Required additional arguments:
        * service
        * environment
        * **Either:**
            * Github username & Github password
            * File path to test.properties file for provided env/svc combo
    * Optional additional argument:
        * host

### Dynamic Inventory Script
Also included in this repository is a dynamic inventory script for use with Ansible and the mopsCompassHiera repository
This can be changed to run on the specified env/svc combos as detailed below.

Add to a command-line run of Ansible by using:

    -i hieraDynInv.py

instead of -i hosts (as above)


Setting up the dynamic inventory variables in group_vars/hieraData.yml - customize as desired per run:
* Set variable hieraFile to correct location
    * **Verify** that the Hiera file in that location contains correct information for your Hiera repository (filepaths to mopsCompassHiera repo are valid, etc.)
* dynInvEnv, dynInvServ, and dynInvServIgnore must be arrays
* dynInvEnv and dynInvServ must have at least one value; dynInvServIgnore may be empty
* dynInvEnv must be filled with valid environment names OR just 'all' (to run against all environments)
* dynInvServ must be filled with valid service names OR just 'all' (to run against all services)
* dynInvServIgnore must be filled with valid service names OR empty
    * Values in this variable are ONLY checked when dynInvServ is 'all'

**NOTE**  These variables _must_ be set within the file specified, as you **cannot** pass arguments to the dynamic inventory script when calling it via Ansible.
