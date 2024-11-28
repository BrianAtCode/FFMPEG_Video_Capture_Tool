from enum import Enum
class TicketPurpose(Enum):
    CAPTURING_TIME = "capturing_time"
    PROGRESS_TIME = "progress_time"
    SPLICE_LENGTH = "splice_length"
    OUTPUT_AUDIO_CODEC = "output_acodec"
    OUTPUT_VIDEO_CODEC = "output_vcodec"
    STATUS = "status"
    CONVERSION_TIME = "conversion_time"
    UI_TABLE_PROGRESS = "ui_table_progress"
    UI_TABLE_STATUS = "ui_table_status"
    UI_TABLE_NEW_TABLE = "ui_table_new_table"
    UI_FORM_INPUT_PATH = "ui_form_input_path"
    UI_FORM_INPUT_VCORDEC = "ui_form_input_vcodec"
    UI_FORM_INPUT_ACODEC = "ui_form_input_acodec"
    UI_FORM_VIDEO_LENGTH = "ui_form_video_length"
    UI_FORM_PROGRESS = "ui_form_progress"
    UI_FORM_CONVERSION_TIME = "ui_form_conversion_time"
    
class Ticket:
    def __init__(self, ticket_id, ticket_type, ticket_value):
        self.ticket_id = ticket_id
        self.ticket_type = ticket_type
        self.ticket_value = ticket_value
