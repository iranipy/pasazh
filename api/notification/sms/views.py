from notification.utils import MetaApiViewClass, JsonValidation

from kavenegar import KavenegarAPI, APIException, HTTPException

from .models import SentSms


class SendSMS(MetaApiViewClass):

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data
        api = KavenegarAPI(self.__sms_api_key)

        try:
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


class SendMassSMS(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data  # https://kavenegar.com/rest.html#sms-sendarray  (parameters)
        api = KavenegarAPI(self.__sms_api_key)

        try:
            res = api.sms_send(data)
            if not isinstance(res, list) or len(res) == 0:
                raise APIException
            for r in res['entries']:
                r['message_id'] = r.pop('messageid')
                r['status_text'] = r.pop('statustext')
                r['sent_date'] = r.pop('date')

                SentSms.objects.create(**r).save()

        except (APIException, HTTPException) as e:
            return self.internal_error(message=[8, str(e)])

        return self.success(data=res, message=[7])


class DeliveryStatus(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        # https://kavenegar.com/rest.html#sms-status
        # https://kavenegar.com/rest.html#sms-statuslocalmessageid
        data = self.request.query_params
        api = KavenegarAPI(self.__sms_api_key)
        try:
            res = api.sms_status(data) if data['message_id'] else api.sms_statuslocalmessageid(data)
        except (APIException, HTTPException) as e:
            return self.internal_error(message=[8, str(e)])

        return self.success(data=res)


class SelectSMS(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        # https://kavenegar.com/rest.html#sms-select
        # https://kavenegar.com/rest.html#sms-selectlatest
        data = self.request.query_params
        api = KavenegarAPI(self.__sms_api_key)
        try:
            res = api.sms_select(data) if data['message_id'] else api.sms_latestoutbox(data)
        except (APIException, HTTPException) as e:
            return self.internal_error(message=[8, str(e)])

        return self.success(data=res)

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def delete(self, request):
        # https://kavenegar.com/rest.html#sms-cancel
        data = self.request.query_params
        api = KavenegarAPI(self.__sms_api_key)
        try:
            res = api.sms_select(data) if data['message_id'] else api.sms_latestoutbox(data)
        except (APIException, HTTPException) as e:
            return self.internal_error(message=[8, str(e)])

        return self.success(data=res)


class SelectSMSInRange(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        # https://kavenegar.com/rest.html#sms-selectoutbox
        data = self.request.query_params
        api = KavenegarAPI(self.__sms_api_key)
        try:
            res = api.sms_selectoutbox(data)
        except (APIException, HTTPException) as e:
            return self.internal_error(message=[8, str(e)])

        return self.success(data=res)


class CountSentSMS(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        # https://kavenegar.com/rest.html#sms-countoutbox
        data = self.request.query_params
        api = KavenegarAPI(self.__sms_api_key)
        try:
            res = api.sms_selectoutbox(data)
        except (APIException, HTTPException) as e:
            return self.internal_error(message=[8, str(e)])

        return self.success(data=res)


class ReceiveSMS(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        # https://kavenegar.com/rest.html#sms-unreads
        data = self.request.query_params
        api = KavenegarAPI(self.__sms_api_key)
        try:
            res = api.sms_selectoutbox(data)
        except (APIException, HTTPException) as e:
            return self.internal_error(message=[8, str(e)])

        return self.success(data=res)

class CountReceiveSMS(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        # https://kavenegar.com/rest.html#sms-countinbox
        data = self.request.query_params
        api = KavenegarAPI(self.__sms_api_key)
        try:
            res = api.sms_selectoutbox(data)
        except (APIException, HTTPException) as e:
            return self.internal_error(message=[8, str(e)])

        return self.success(data=res)
