import spcloud
from spcloud import *
card = '注册卡密'
charger_card = r'充值卡密'
user = r'user'
passwd = r'passwd'

a = sp_cloud_create()

sp_cloud_set_conninfo(a, '默认软件', '0.0.0.0', 8897, 300, c_bool(False))


login = sp_user_login(a, user, passwd)
print(login)

user = sp_cloud_get_user(a)
print(user)

beat = sp_cloud_beat(a)
print(beat)

agent = sp_cloud_get_card_agent(a)
print(agent)

card_type = sp_cloud_get_card_type(a)
print(card_type)

login_ip = sp_cloud_get_ip_address(a)
print(login_ip)

remarks = sp_cloud_get_remarks(a)
print(remarks)

create_time_stamp = sp_cloud_get_created_time_stamp(a)
print(create_time_stamp)

activated_time_stamp = sp_cloud_get_activated_time_stamp(a)
print(activated_time_stamp)

expired_time_stamp = sp_cloud_get_expired_time_stamp(a)
print(expired_time_stamp)

old_point = sp_cloud_get_fyi(a)
print(old_point)

deduct_fyi = sp_cloud_deduct_fyi(a, 1)
print(deduct_fyi)

new_point = sp_cloud_get_fyi(a)
print(new_point)

open_max_num = sp_cloud_get_open_max_num(a)
print(open_max_num)

bind = sp_cloud_get_bind(a)
print(bind)

bind_time = sp_cloud_get_bind_time(a)
print(bind_time)

unbind_deduct_time = sp_cloud_get_unbind_deduct_time(a)
print(unbind_deduct_time)

unbind_max_num = sp_cloud_get_unbind_max_num(a)
print(unbind_max_num)

unbind_count_total = sp_cloud_get_unbind_count_total(a)
print(unbind_count_total)

unbind_deduct_time_total = sp_cloud_get_unbind_deduct_time_total(a)
print(unbind_deduct_time_total)

notice = sp_cloud_get_notices(a)
print(notice)

cards = sp_cloud_get_card(a)
print(cards)

CID = sp_cloud_get_cid(a)
print(CID)

online_count = sp_cloud_get_online_count(a)
print(online_count)

# win_ver = sp_cloud_set_win_ver(a)
# print(win_ver)

pc_sign = sp_cloud_get_pc_sign(a)
print(pc_sign)

unbind_count = sp_cloud_get_unbind_count(a)
print(unbind_count)

update_info = sp_cloud_get_update_info(a)
print(update_info)

# local_ver_number = sp_cloud_get_local_ver_number(a)
# print(local_ver_number)

online_total_count = sp_cloud_get_online_total_count(a)
print(online_total_count)

online_cards_count = sp_cloud_get_online_cards_count(a)
print(online_cards_count)

online_count_by_card = sp_cloud_get_online_count_by_card(a, '')
print(online_count_by_card)

target_pc_sign = sp_cloud_user_query_pc_sign(a, user, passwd)
print(target_pc_sign)

remove_pc_sign = sp_cloud_user_remove_pc_sign(a, user, passwd, pc_sign['pc_sign'], 1)
print(remove_pc_sign)

query_online = sp_cloud_user_query_online(a, user, passwd)
print(query_online)

close_online_by_cid = sp_cloud_user_close_online_by_cid(a, user, passwd , CID['cid'])
print(close_online_by_cid)

trail_card = sp_cloud_apply_trial_card(a)
print(trail_card)

basic_info = sp_cloud_get_basic_info(a)
print(basic_info)

# 注册，改密，充值
# register = sp_cloud_user_register(a, user, passwd, 'super passwd', card)
# print(register)
#
# charge = sp_cloud_user_recharge(a, user, charger_card)
# print(charge)
#
# change_passwd = sp_cloud_user_change_pwd(a, user, 'super passwd', 'new passwd')
# print(change_passwd)
#
# retrieve_passwd = sp_cloud_retrieve_password(a, card)
# print(retrieve_passwd)

# 禁用卡密
# disable_card = sp_cloud_disable_card(a)
# print(disable_card)

sp_cloud_offline(a)
sp_cloud_destroy(a)

