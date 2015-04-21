#check cluster status
from eayunstack_tools.doctor import common
from eayunstack_tools.utils import NODE_ROLE, get_controllers_hostname
from eayunstack_tools.doctor.cls_func import get_rabbitmq_nodes, get_mysql_nodes, get_haproxy_nodes, get_ceph_health, get_ceph_osd_status
import logging

LOG = logging.getLogger(__name__)

def cls(parser):
    print "check cluster module"
    if parser.CHECK_ALL:
        check_all()
    if parser.CLUSTER_NAME == 'rabbitmq':
        check_rabbitmq()
    if parser.CLUSTER_NAME == 'mysql':
        check_mysql()
    if parser.CLUSTER_NAME == 'haproxy':
        check_haproxy()
    if parser.CLUSTER_NAME == 'ceph':
        check_ceph()

def make(parser):
    '''Check cluster'''
    parser.add_argument(
        '-n',
        dest='CLUSTER_NAME',
        choices=['mysql','rabbitmq','ceph','haproxy'],
        help='Cluster Name',
    )
    common.add_common_opt(parser)
    parser.set_defaults(func=cls)

def check_all():
    '''Check All Cluster'''
    print "Check All Cluster"

def check_rabbitmq():
    # node role check
    if not NODE_ROLE.is_fuel():
        if not NODE_ROLE.is_controller():
            LOG.warn('This command can only run on fuel or controller node !')
            return
    # get all controller node hostname
    controllers = get_controllers_hostname()
    if controllers is None:
        LOG.error('Can not get the controllers node list !')
        return
    # get masters & slaves node list
    masters = get_rabbitmq_nodes('masters')
    slaves = get_rabbitmq_nodes('slaves')
    running_nodes = masters + slaves
    if running_nodes is None:
        LOG.error('Can not get the running node list for rabbitmq cluster !')
        return
    # check all controller nodes in masters + slaves node list
    error_nodes = []
    for node in controllers:
        if node not in running_nodes:
            error_nodes.append(node)

    if error_nodes:
        LOG.error('Node %s not in rabbitmq cluster !' % error_nodes)
        LOG.error('Rabbitmq cluster check faild !')
    else:
        LOG.info('Rabbitmq cluster check successfully !')

def check_mysql():
    print 'check mysql'
    # node role check
    if not NODE_ROLE.is_fuel():
        if not NODE_ROLE.is_controller():
            LOG.warn('This command can only run on fuel or controller node !')
            return
    # get running node list for mysql cluster
    running_nodes = get_mysql_nodes()
    if running_nodes is None:
        LOG.error('Can not get the running node list for rabbitmq cluster !')
        return
    # get all controller node hostname
    controllers = get_controllers_hostname()
    if controllers is None:
        LOG.error('Can not get the controllers node list !')
        return
    # check all controller node in mysql cluster
    error_nodes = []
    for node in controllers:
        if node not in running_nodes:
            error_nodes.append(node)

    if error_nodes:
        LOG.error('Node %s is not running in mysql cluster !' % error_nodes)
        LOG.error('Mysql cluster check faild !')
    else:
        LOG.info('Mysql cluster check successfully !')

def check_haproxy():
    print 'check haproxy'
    # node role check
    if not NODE_ROLE.is_fuel():
        if not NODE_ROLE.is_controller():
            LOG.warn('This command can only run on fuel or controller node !')
            return
    # get running node list for mysql cluster
    running_nodes = get_haproxy_nodes()
    if running_nodes is None:
        LOG.error('Can not get the running node list for haproxy cluster !')
        return
    # get all controller node hostname
    controllers = get_controllers_hostname()
    if controllers is None:
        LOG.error('Can not get the controllers node list !')
        return
    # check all controller node in mysql cluster
    error_nodes = []
    for node in controllers:
        if node not in running_nodes:
            error_nodes.append(node)

    if error_nodes:
        LOG.error('Node %s is not running in haproxy cluster !' % error_nodes)
        LOG.error('Haproxy cluster check faild !')
    else:
        LOG.info('Haproxy cluster check successfully !')

def check_ceph():
    print 'check ceph'
    # node role check
    if not NODE_ROLE.is_fuel():
        if not NODE_ROLE.is_controller():
            if not NODE_ROLE.is_ceph_osd():
                LOG.warn('This command can only run on fuel or controller or ceph-osd node !')
                return
    # get cluster status
    LOG.info('%s Checking ceph cluster status %s' %('='*10, '='*10))
    if get_ceph_health():
        LOG.info('Ceph cluster check successfully !')    
    else:
        LOG.error('Ceph cluster check faild !')
    # check osd status
    LOG.info('%s Checking ceph osd status %s' %('='*10, '='*10))
    check_success = True
    osd_status = get_ceph_osd_status()
    if not osd_status:
        LOG.error('Can not get ceph osd status !')
    else:
        for l in osd_status.split('\n'):
            if 'id' not in l and 'weigh' not in l and 'osd.' in l:
                osd = l.split()[2]
                status = l.split()[3]
                if status != 'up':
                    LOG.error('%s status is not correct, please check it !', osd)
                    check_success = False
    if check_success:
        LOG.info('Ceph osd status check successfully !')
