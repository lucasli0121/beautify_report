'''
Author: liguoqiang
Date: 2025-04-15 21:00:10
LastEditors: liguoqiang
LastEditTime: 2025-04-17 19:44:46
Description: 
'''
from typing import Callable
from nicegui import ui
import pandas as pd

from typing import Optional

import_excel_callback: Optional[Callable] = None

def handle_upload(event):
    # event.content 是文件的二进制内容
    import io
    file_content = io.BytesIO(event.content.read())
    d = pd.read_excel(file_content, sheet_name=None)
    if import_excel_callback is not None:
        import_excel_callback(d)

def handle_muliple_upload(event):
    # event.content 是文件的二进制内容
    pass

def open_import_excel_dialog(handle_excel: Callable):
    global import_excel_callback
    import_excel_callback = handle_excel
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/3 h-1/3') \
            .style('background-color: #FFFFFF !important; border-radius: 10px;'):
            with ui.row().classes('size-full mt-5 place-content-between'):
                with ui.upload(label="请选择批量上传设备文件", on_upload=handle_upload) \
                    .props('flat accept=".xls,.xlsx"') \
                    .classes('size-full') as upload:
                    upload.add_slot('header="scope"', r'''
                        <template #header="scope">
                            <div class="row no-wrap items-center q-pa-sm q-gutter-xs">
                            <q-btn v-if="scope.queuedFiles.length > 0" icon="clear" @click="scope.removeQueuedFiles" round dense flat >
                                <q-tooltip>Clear All</q-tooltip>
                            </q-btn>
                            <q-btn v-if="scope.uploadedFiles.length > 0" icon="done_all" @click="scope.removeUploadedFiles" round dense flat >
                                <q-tooltip>Remove Uploaded Files</q-tooltip>
                            </q-btn>
                            <q-spinner v-if="scope.isUploading" class="q-uploader__spinner" />
                            <div class="col">
                                <div class="q-uploader__title">Upload your files</div>
                                <div class="q-uploader__subtitle">{{ scope.uploadSizeLabel }} / {{ scope.uploadProgressLabel }}</div>
                            </div>
                            <q-btn v-if="scope.canAddFiles" type="a" icon="add_box" @click="scope.pickFiles" round dense flat>
                                <q-uploader-add-trigger />
                                <q-tooltip>Pick Files</q-tooltip>
                            </q-btn>
                            <q-btn v-if="scope.canUpload" icon="cloud_upload" @click="scope.upload" round dense flat >
                                <q-tooltip>Upload Files</q-tooltip>
                            </q-btn>

                            <q-btn v-if="scope.isUploading" icon="clear" @click="scope.abort" round dense flat >
                                <q-tooltip>Abort Upload</q-tooltip>
                            </q-btn>
                            </div>
                        </template>
                    ''')

    dialog.open()