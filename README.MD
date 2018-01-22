# Benny Kopilov
# Prerequisites:
```
HOME_DIR=/home/stack


easy_install pip
pip install virtualenv
virtualenv .venv
source .venv/bin/activate

cd $HOME_DIR
git clone https://github.com/openstack/tempest.git
pip install -r  $HOME_DIR/tempest/test-requirements.txt -r $HOME_DIR/tempest/requirements.txt
git config --global http.sslVerify false
git clone https://github.com/bkopilov/tempest_common_plugin.git
cd $HOME_DIR/tempest_common_plugin
# install downstream plugin under tempest
pip install --upgrade -e .
```

###  we assume that tempest.conf aready configured manually or with a script .

```
TEMPEST_FILE=/home/stack/tempest/etc/tempest.conf

## create tempest account.yaml to run tests with demo tenants.
source $HOME_DIR/overcloudrc
wget http://storage-jenkins.scl.lab.tlv.redhat.com/accounts.yaml $HOME_DIR
sed -i -e "s/test/$OS_PASSWORD/g" $HOME_DIR/accounts.yaml
sudo yum install -y crudini
crudini --set $TEMPEST_FILE auth test_accounts_file /home/stack/accounts.yaml
```


## get a list of all tests
```
cd $HOME_DIR/tempest
testr init
testr list-tests
```
run a test from the list

By default tempest runs with dynamic credentials

(creates a tenant / user/ network for each testcase)

testr run [path for the testcase]


In order to run a tempest tests with demo user, modify use_dynamic_credentials to False.

Example for capture overcloud:

crudini --set $TEMPEST_FILE auth use_dynamic_credentials false

crudini --set $TEMPEST_FILE oslo_concurrency lock_path /tmp/tempest_lock


```
 testr run tempest_common_plugin.tests.scenario.prepare_cloud.test_prepare_cloud.PrepareCloudActions --subunit | tee >(subunit2junitxml --output-to=$HOME_DIR/tempest1.xml) | subunit-2to1
 rm -rf /tmp/tempest_lock

# Example for verify cloud capture
 rm -rf /tmp/tempest_lock
 crudini --set $TEMPEST_FILE auth use_dynamic_credentials false
 testr run tempest_common_plugin.tests.scenario.prepare_cloud.test_verify_cloud.VerifyCloudActions --subunit | tee >(subunit2junitxml --output-to=$HOME_DIR/tempest2.xml) | subunit-2to1

# Example for post verify actions
 rm -rf /tmp/tempest_lock
 crudini --set $TEMPEST_FILE auth use_dynamic_credentials false
 testr run tempest_common_plugin.tests.scenario.prepare_cloud.test_post_cloud.PostCloudActions --subunit | tee >(subunit2junitxml --output-to=$HOME_DIR/tempest3.xml) | subunit-2to1
#
 crudini --set $TEMPEST_FILE auth use_dynamic_credentials true
```


