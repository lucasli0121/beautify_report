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
        {'name': 'brief_name', 'label': '简称', 'field': 'brief_name', 'width': '5%', 'align': 'center'},
        {'name': 'address', 'label': '地址', 'field': 'address', 'width': '15%', 'align': 'center'},
        {'name': 'contacts', 'label': '联系人', 'field': 'contacts', 'width': '10%', 'align': 'center'},
        {'name': 'phone', 'label': '电话', 'field': 'phone', 'width': '10%', 'align': 'center'},
        {'name': 'email', 'label': '邮箱', 'field': 'email', 'width': '10%', 'align': 'center'},
        {'name': 'invoice_limit', 'label': '开票额度', 'field': 'invoice_limit', 'width': '5%', 'align': 'center'},
        {'name': 'has_invoiced', 'label': '已开票', 'field': 'has_invoiced', 'width': '5%', 'align': 'center'},
        {'name': 'tax_no', 'label': '税号', 'field': 'tax_no', 'width': '10%', 'align': 'center'},
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
        table.props('visible-columns="[\'sn\', \'name\', \'brief_name\', \'address\', \'contacts\', \'phone\', \'email\', \'invoice_limit\', \'has_invoiced\', \'tax_no\', \'operation\']"')
        
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
# @description: 显示开票的表格
# @param {list} datas 数据列表
#
def show_open_invoice_table(datas, show_delete) -> ui.table:
    table_columns = [
        {'name': 'id', 'label': 'id', 'field': 'id', 'width': '1%', 'align': 'center'},
        {'name': 'sn', 'label': '排名', 'field': 'sn', 'width': '5%', 'align': 'center'},
        {'name': 'from_company_name', 'label': '开票方', 'field': 'from_company_name', 'width': '10%', 'align': 'center'},
        {'name': 'to_company_name', 'label': '受票方', 'field': 'to_company_name', 'width': '10%', 'align': 'center'},
        {'name': 'invoice_type', 'label': '发票类型', 'field': 'invoice_type', 'width': '5%', 'align': 'center'},
        {'name': 'invoice_content', 'label': '发票内容', 'field': 'invoice_content', 'width': '5%', 'align': 'center'},
        {'name': 'before_tax_money', 'label': '税前额', 'field': 'before_tax_money', 'width': '10%', 'align': 'center'},
        {'name': 'tax_rate', 'label': '税率', 'field': 'tax_rate', 'width': '5%', 'align': 'center'},
        {'name': 'invoice_money', 'label': '开票额', 'field': 'invoice_money', 'width': '10%', 'align': 'center'},
        {'name': 'added_tax', 'label': '增值税额', 'field': 'added_tax', 'width': '10%', 'align': 'center'},
        {'name': 'contract_content', 'label': '合同内容', 'field': 'contract_content', 'width': '10%', 'align': 'center'},
        {'name': 'create_time', 'label': '开票时间', 'field': 'create_time', 'width': '10%', 'align': 'center'},
        {'name': 'operation', 'label': '操作', 'field': 'operation', 'width': '10%', 'align': 'center'}
    ]
    with ui.table(
        columns=table_columns,
        rows=datas,
        selection='multiple',
        row_key='name',
        pagination={'rowsPerPage': 10, 'sortBy': 'sn', 'page': 1}) \
            .props('table-header-style="color: white; font-size: 16px; background-color: #65B6FF;" flat no-shadow') \
            .classes('w-full mt-2 gap-0') \
            .style('border: 1px solid #ECECEC; border-radius: 10px 10px 0px 0px;') as table:
        
        table.props('v-model:selected="selected"')
        table.props('visible-columns="[ \
                    \'sn\', \
                    \'from_company_name\', \
                    \'to_company_name\', \
                    \'invoice_type\', \
                    \'invoice_content\', \
                    \'before_tax_money\', \
                    \'tax_rate\', \
                    \'invoice_money\', \
                    \'added_tax\', \
                    \'contract_content\', \
                    \'create_time\', \
                    \'operation\']"')

        table.add_slot('body-cell-invoice_type', r'''
            <q-td auto-width key="invoice_type" :props="props">  
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

#
# @description: 显示公司银行账户表格
# @param {list} datas 数据列表
# @param {function} show_delete 删除操作的回调函数
#
def show_company_bank_account_table(datas, show_delete) -> ui.table:
    table_columns = [
        {'name': 'id', 'label': 'id', 'field': 'id', 'width': '0%', 'align': 'center'},
        {'name': 'sn', 'label': '序号', 'field': 'sn', 'width': '5%', 'align': 'center'},
        {'name': 'name', 'label': '公司名称', 'field': 'name', 'width': '10%', 'align': 'center'},
        {'name': 'bank_account', 'label': '银行账户', 'field': 'bank_account', 'width': '10%', 'align': 'center'},
        {'name': 'bank_name', 'label': '银行名称', 'field': 'bank_name', 'width': '15%', 'align': 'center'},
        {'name': 'account_type', 'label': '账号类型', 'field': 'account_type', 'width': '10%', 'align': 'center'},
        {'name': 'bank_address', 'label': '银行地址', 'field': 'bank_address', 'width': '25%', 'align': 'center'},
        {'name': 'operation', 'label': '操作', 'field': 'operation', 'width': '10%', 'align': 'center'}
    ]
    with ui.table(
        columns=table_columns,
        rows=datas,
        row_key='id',
        pagination={'rowsPerPage': 10, 'sortBy': 'sn', 'page': 1}) \
            .props('table-header-style="color: white; font-size: 16px; background-color: #65B6FF;"') \
            .classes('w-full mt-2 gap-0') \
            .style('border: 1px solid #ECECEC; border-radius: 10px 10px 0px 0px;') as table:
        table.props('v-model:selected="selected"')
        table.props('visible-columns="[\'sn\', \'name\', \'bank_account\', \'bank_name\', \'account_type\', \'bank_address\', \'operation\']"')
        
        table.add_slot('body-cell-account_type', r'''
            <q-td auto-width key="account_type" :props="props">  
                <template v-if="props.row.account_type == 0">
                    基本户
                </template>
                <template v-if="props.row.account_type == 1">
                    一般户
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

#
# @description: 显示付款记录表格
# @param {list} datas 数据列表
#
def show_payment_record_table(datas, show_delete) -> ui.table:
    table_columns = [
        {'name': 'id', 'label': 'id', 'field': 'id', 'width': '0%', 'align': 'center'},
        {'name': 'sn', 'label': '排名', 'field': 'sn', 'width': '5%', 'align': 'center'},
        {'name': 'from_company_name', 'label': '付款方', 'field': 'from_company_name', 'width': '10%', 'align': 'center'},
        {'name': 'to_company_name', 'label': '受款方', 'field': 'to_company_name', 'width': '10%', 'align': 'center'},
        {'name': 'payment_money', 'label': '付款金额', 'field': 'payment_money', 'width': '10%', 'align': 'center'},
        {'name': 'total_invoice_money', 'label': '应开票金额', 'field': 'total_invoice_money', 'width': '10%', 'align': 'center'},
        {'name': 'has_invoice_money', 'label': '已开票金额', 'field': 'has_invoice_money', 'width': '10%', 'align': 'center'},
        {'name': 'remain_invoice_money', 'label': '未开票金额', 'field': 'remain_invoice_money', 'width': '10%', 'align': 'center'},
        {'name': 'invoice_content', 'label': '开票内容', 'field': 'invoice_content', 'width': '5%', 'align': 'center'},
        {'name': 'status', 'label': '状态', 'field': 'status', 'width': '10%', 'align': 'center'},
        {'name': 'create_time', 'label': '付款时间', 'field': 'create_time', 'width': '10%', 'align': 'center'},
        {'name': 'operation', 'label': '操作', 'field': 'operation', 'width': '10%', 'align': 'center'}
    ]
    with ui.table(
        columns=table_columns,
        rows=datas,
        selection='multiple',
        row_key='name',
        pagination={'rowsPerPage': 10, 'sortBy': 'sn', 'page': 1}) \
            .props('table-header-style="color: white; font-size: 16px; background-color: #65B6FF;" flat no-shadow') \
            .classes('w-full mt-2 gap-0') \
            .style('border: 1px solid #ECECEC; border-radius: 10px 10px 0px 0px;') as table:
        
        table.props('v-model:selected="selected"')
        table.props('visible-columns="[ \
                    \'sn\', \
                    \'from_company_name\', \
                    \'to_company_name\', \
                    \'payment_money\', \
                    \'total_invoice_money\', \
                    \'has_invoice_money\', \
                    \'remain_invoice_money\', \
                    \'invoice_content\', \
                    \'status\', \
                    \'create_time\', \
                    \'operation\']"')

        table.add_slot('body-cell-status', r'''
            <q-td auto-width key="status" :props="props">  
                <template v-if="props.row.status == 0">
                    未完成
                </template>
                <template v-if="props.row.status == 1">
                    已完成
                </template>
                <template v-if="props.row.status == 1">
                    已取消
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