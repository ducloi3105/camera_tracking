from src.bases.databases.models import Model
from src.bases.models import fields
from src.common.constants import STRING_LENGTH


class MicrophoneMapping(Model):
    name = fields.String(max_length=STRING_LENGTH['EX_SHORT'],
                         required=True)
