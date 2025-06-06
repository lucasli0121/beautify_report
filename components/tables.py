'''
Author: liguoqiang
Date: 2025-03-15 09:47:54
LastEditors: liguoqiang
LastEditTime: 2025-03-15 23:10:29
Description: 
'''
from nicegui import ui

def show_company_table(datas, show_detail, show_delete) -> ui.table:
    table_columns = [
        {'name': 'id', 'label': 'id', 'field': 'id', 'width': '0%', 'align': 'center'},
        {'name': 'sn', 'label': '序号', 'field': 'sn', 'width': '5%', 'align': 'center'},
        {'name': 'name', 'label': '名称', 'field': 'name', 'width': '10%', 'align': 'center'},
        {'name': 'address', 'label': '地址', 'field': 'address', 'width': '10%', 'align': 'center'},
        {'name': 'contacts', 'label': '联系人', 'field': 'contacts', 'width': '10%', 'align': 'center'},
        {'name': 'phone', 'label': '电话', 'field': 'phone', 'width': '15%', 'align': 'center'},
        {'name': 'email', 'label': '邮箱', 'field': 'email', 'width': '15%', 'align': 'center'},
        {'name': 'invoice_limit', 'label': '开票额度', 'field': 'invoice_limit', 'width': '10%', 'align': 'center'},
        {'name': 'has_invoiced', 'label': '已开票', 'field': 'has_invoiced', 'width': '10%', 'align': 'center'},
        {'name': 'tax_id', 'label': '税号', 'field': 'tax_id', 'width': '10%', 'align': 'center'},
        {'name': 'operation', 'label': '操作', 'field': 'operation', 'width': '10%', 'align': 'center'}
    ]
    with ui.table(
        columns=table_columns,
        rows=datas,
        row_key='id',
        selection='multiple',
        pagination={'rowsPerPage': 10, 'sortBy': 'sn', 'page': 1}) \
            .props('table-header-style="color: white; font-size: 16px; background-color: #65B6FF;"') \
            .classes('w-full mt-2 gap-0') \
            .style('border: 1px solid #ECECEC; border-radius: 10px 10px 0px 0px;') as table:
        # table.add_slot('header', r'''
        #     <q-tr :props="props" class="table-header">
        #         <q-th v-for="col in props.cols" :key="col.name" :props="props">
        #             {{ col.label }}
        #         </q-th>
        #     </q-tr>
        # ''')
        table.props('v-model:selected="selected"')
        table.props('visible-columns="[\'sn\', \'name\', \'address\', \'contacts\', \'phone\', \'email\', \'invoice_limit\', \'has_invoiced\', \'tax_id\', \'operation\']"')
        
        table.add_slot('body-cell-operation', r'''
            <q-td auto-width key="operation" :props="props" class="item-left">
                <q-btn size="sm" flat round dense icon="img:/static/images/report_mini.png"
                    @click="() => $parent.$emit('show_detail', props.row)"
                />
                <span style="display: inline-block; width: 5px;"></span>
                <q-btn size="sm" flat round dense icon="img:/static/images/delete_mini.png"
                    @click="() => $parent.$emit('show_delete', props.row)"
                />
            </q-td>
        ''')
        table.on('show_detail', show_detail)
        table.on('show_delete', show_delete)
    return table

#
# @description: 显示班级报表中的表格
# @param {list} datas 数据列表
#
def show_open_invoice_table(datas, show_delete) -> ui.table:
    table_columns = [
        {'name': 'id', 'label': 'id', 'field': 'id', 'width': '1%', 'align': 'center'},
        {'name': 'sn', 'label': '排名', 'field': 'sn', 'width': '5%', 'align': 'center'},
        {'name': 'invoice_from', 'label': '开票方', 'field': 'invoice_from', 'width': '10%', 'align': 'center'},
        {'name': 'invoice_to', 'label': '受票方', 'field': 'invoice_to', 'width': '10%', 'align': 'center'},
        {'name': 'invoice_type', 'label': '发票类型', 'field': 'invoice_type', 'width': '5%', 'align': 'center'},
        {'name': 'invoice_money', 'label': '开票额', 'field': 'mid_concentration', 'width': '10%', 'align': 'center'},
        {'name': 'tax_rate', 'label': '税率', 'field': 'tax_rate', 'width': '5%', 'align': 'center'},
        {'name': 'invoice_content', 'label': '发票内容', 'field': 'invoice_content', 'width': '5%', 'align': 'center'},
        {'name': 'contract_content', 'label': '合同内容', 'field': 'contract_content', 'width': '10%', 'align': 'center'},
        {'name': 'before_tex_money', 'label': '税前额', 'field': 'before_tex_money', 'width': '10%', 'align': 'center'},
        {'name': 'added_tex', 'label': '增值税', 'field': 'added_tex', 'width': '10%', 'align': 'center'},
        {'name': 'create_time', 'label': '开票时间', 'field': 'create_time', 'width': '10%', 'align': 'center'},
        {'name': 'operation', 'label': '操作', 'field': 'operation', 'width': '10%', 'align': 'center'}
    ]
    with ui.table(
        columns=table_columns,
        rows=datas,
        row_key='name',
        pagination={'rowsPerPage': 10, 'sortBy': 'sn', 'page': 1}) \
            .props('table-header-style="color: white; font-size: 16px; background-color: #65B6FF;" flat no-shadow') \
            .classes('w-full mt-2 gap-0') \
            .style('border: 1px solid #ECECEC; border-radius: 10px 10px 0px 0px;') as table:
        
        table.props('visible-columns="[ \
                    \'sn\', \
                    \'invoice_from\', \
                    \'invoice_to\', \
                    \'invoice_type\', \
                    \'invoice_money\', \
                    \'tax_rate\', \
                    \'invoice_content\', \
                    \'contract_content\', \
                    \'before_tex_money\', \
                    \'added_tex\', \
                    \'create_time\', \
                    \'operation\']"')

        table.add_slot('body-cell-invoice_type', r'''
            <q-td auto-width key="gender" :props="props">  
                <template v-if="props.row.invoice_type == 0">
                    普票
                </template>
                <template v-if="props.row.invoice_type == 1">
                    专票
                </template>
            </q-td>
        ''')
        table.add_slot('body-cell-operation', r'''
            <q-td auto-width key="operation" :props="props" class="item-left">
                <q-btn size="sm" flat round dense icon="img:/static/images/delete_mini.png"
                    @click="() => $parent.$emit('show_delete', props.row)"
                />
            </q-td>
        ''')
        table.on('show_delete', show_delete)
    return table

def show_devices_table(datas, on_device_edit, on_device_delete) -> ui.table:
    columns = [
        {'name': 'sn', 'label': '序号', 'field': 'sn', 'width': '5%', 'align': 'center'},
        {'name': 'seat_no', 'label': '座位号', 'field': 'seat_no', 'width': '5%', 'align': 'center'},
        {'name': 'mac', 'label': '设备码', 'field': 'mac', 'width': '10%', 'align': 'center'},
        {'name': 'is_installed', 'label': '状态', 'field': 'is_installed', 'width': '10%', 'align': 'center'},
        {'name': 'is_online', 'label': '在线', 'field': 'is_online', 'width': '10%', 'align': 'center'},
        {'name': 'operation', 'label': '操作', 'field': 'operation', 'width': '20%', 'align': 'center'}
    ]
    with ui.table(
        columns=columns,
        rows=datas,
        row_key='seat_no',
        selection='multiple',
        pagination={'rowsPerPage': 10, 'sortBy': 'sn', 'page': 1}) \
            .props('table-header-style="color: white; font-size: 16px; background-color: #65B6FF;"') \
            .classes('w-full mt-2 gap-0 no-shadow') \
            .style('border: 1px solid #ECECEC; border-radius: 10px 10px 0px 0px;') as table:
        table.props('v-model:selected="selected"')
        # table.add_slot('header', r'''
        #     <q-tr :props="props" class="table-header">
        #         <q-th :style="`width: 10%;`" />
        #         <q-th v-for="col in props.cols" :key="col.name" :props="props" :style="`width: ${col.width};`">
        #             {{ col.label }}
        #         </q-th>
        #     </q-tr>
        # ''')
        table.add_slot('body-cell-is_installed', r'''
            <q-td auto-width key="is_installed" :props="props">
                <template v-if="props.row.is_installed == 0">
                    <div style="text-align: center; width: 50px; height: 30px; line-height: 30px; background-color: #FF8787; border-radius: 17px;">
                       <font style="font-size: 12px; color: white;">未安装</font>
                    </div>
                </template>
                <template v-else>
                    <div style="text-align: center; width: 50px; height: 30px; line-height: 30px; background-color: #27CACA; border-radius: 17px;">
                       <font style="font-size: 12px; color: white;">已安装</font>
                    </div>
                </template>
            </q-td>
        ''')
        table.add_slot('body-cell-is_online', r'''
            <q-td auto-width key="is_online" :props="props">
                <template v-if="props.row.is_online == -1">
                    <div style="text-align: center; width: 50px; height: 30px; line-height: 30px; background-color: #FF8787; border-radius: 17px;">
                       <font style="font-size: 12px; color: white;">未绑定</font>
                    </div>
                </template>
                <template v-if="props.row.is_online == 0">
                    <div style="text-align: center; width: 50px; height: 30px; line-height: 30px; background-color: #C5C5C5; border-radius: 17px;">
                       <font style="font-size: 12px; color: white;">离线</font>
                    </div>
                </template>
                <template v-else>
                    <div style="text-align: center; width: 50px; height: 30px; line-height: 30px; background-color: #27CACA; border-radius: 17px;">
                       <font style="font-size: 12px; color: white;">在线</font>
                    </div>
                </template>
            </q-td>
        ''')
        table.add_slot('body-cell-operation', r'''
            <q-td auto-width key="operation" :props="props">
                <!--
                <q-btn size="sm" round dense icon="edit"
                    @click="() => $parent.$emit('on_device_edit', props.row)"
                />
                <span style="display: inline-block; width: 5px;"></span>
                -->
                <q-btn size="sm" flat round dense icon="img:/static/images/delete_mini.png"
                    @click="() => $parent.$emit('on_device_delete', props.row)"
                />
            </q-td>
        ''')
        table.on('on_device_edit', on_device_edit)
        table.on('on_device_delete', on_device_delete)
    return table