# Benny Kopilov
# Prerequisites:

# git clone tempest upstream code
git clone https://github.com/openstack/tempest.git
cd tempest

# git clone plugin code

USERNAME=`whoami` 
git clone ssh://$USERNAME@code.engineering.redhat.com:22/rhos-qe-tests/tempest_common_plugin

cd tempest_common_plugin/tempest_plugin

# install python packages

sudo pip install --upgrade -e .

# Verify testr list-tests and run:

cd tempest/

testr init

testr list-tests | grep -i storage

testr run [test_name]

