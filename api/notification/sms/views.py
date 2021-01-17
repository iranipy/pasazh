from sms import api
from .utils import MetaApiViewClass


class SendSMS(MetaApiViewClass):
    @MetaApiViewClass.generic_decor
    def post(self, request):
        data = self.request.data
        sender = data['sender']
        receiver = data['receiver']
        message = data['msg']
        params = {
            'sender': sender,
            'receptor': receiver,
            'message': message
        }
        response = api.sms_send(params)

        return self.success(data=response)
