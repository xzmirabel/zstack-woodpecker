'''

Test load balance. 

Test step:
    1. Create 2 VM with load balance l3 network service.
    2. Create a LB with 2 VMs' nic
    3. Check the LB 
    4. Destroy VMs

@author: Youyk
'''
import os

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_load_balancer \
        as zstack_lb_header

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm with lb.')
    vm1 = test_stub.create_lb_vm()
    test_obj_dict.add_vm(vm1)
    vm2 = test_stub.create_lb_vm()
    test_obj_dict.add_vm(vm2)
    
    #l3_name = os.environ.get('l3VlanNetworkName1')
    #vr1 = test_stub.get_vr_by_private_l3_name(l3_name)

    #l3_name = os.environ.get('l3NoVlanNetworkName1')
    #vr2 = test_stub.get_vr_by_private_l3_name(l3_name)

    vm_nic1 = vm1.get_vm().vmNics[0]
    vm_nic1_uuid = vm_nic1.uuid
    vm_nic2 = vm2.get_vm().vmNics[0]
    vm_nic2_uuid = vm_nic2.uuid
    pri_l3_uuid = vm_nic1.l3NetworkUuid

    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
    l3_uuid = vr_pub_nic.l3NetworkUuid

    vip = test_stub.create_vip('vip_for_lb_test', l3_uuid)
    test_obj_dict.add_vip(vip)

    lb = zstack_lb_header.ZstackTestLoadBalancer()
    lb.create('create lb test', vip.get_vip().uuid)
    test_obj_dict.add_load_balancer(lb)

    lb_creation_option = test_lib.lib_create_lb_listener_option()

    lbl = lb.create_listener(lb_creation_option)

    lbl.add_nics([vm_nic1_uuid, vm_nic2_uuid])

    vm1.check()
    vm2.check()

    lb.check()
    lb.delete()
    test_obj_dict.rm_load_balancer(lb)
    lb.check()
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create Load Balancer Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
