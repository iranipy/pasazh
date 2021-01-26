from notification.utils import MetaApiViewClass, JsonValidation

from os import getenv
from kavenegar import KavenegarAPI, APIException, HTTPException
from .models import SentSms


class SendSMS(MetaApiViewClass):

    __sms_api_key = getenv("SMS_API_KEY")

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data
        api = KavenegarAPI(self.__sms_api_key)

        try:
            print(data)
            res = api.sms_send(data)
            if not isinstance(res, list) or len(res) == 0:
                raise APIException

            for r in res:
                r['message_id'] = r.pop('messageid')
                r['status_text'] = r.pop('statustext')
                r['sent_date'] = r.pop('date')

                SentSms.objects.create(**r).save()

                if r['status'] != 1:
                    raise APIException

        except (APIException, HTTPException) as e:
            return self.internal_error(message=[8, str(e)])

        return self.success(data=res, message=[7])
