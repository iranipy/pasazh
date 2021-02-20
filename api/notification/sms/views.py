from os import getenv
from kavenegar import KavenegarAPI, APIException, HTTPException

from notification.utils import MetaApiViewClass, JsonValidation, Helpers
from .models import SentSms


class ViewTemplate(MetaApiViewClass):
    _sms_api_key = getenv("SMS_API_KEY")


class SendSMS(ViewTemplate):

    @ViewTemplate.generic_decor()
    @JsonValidation.validate
    def post(self, request):
        """sms-send

        https://kavenegar.com/rest.html#sms-send
        """

        data = self.request.data
        api = KavenegarAPI(self._sms_api_key)

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


class SendMassSMS(ViewTemplate):

    @ViewTemplate.generic_decor()
    @JsonValidation.validate
    def post(self, request):
        """sms-sendarray

        https://kavenegar.com/rest.html#sms-sendarray
        """

        data = self.request.data
        api = KavenegarAPI(self._sms_api_key)

        try:
            res = api.sms_sendarray(data)
            if not isinstance(res, list) or len(res) == 0:
                raise APIException

            for r in res:
                r['message_id'] = r.pop('messageid')
                r['status_text'] = r.pop('statustext')
                r['sent_date'] = r.pop('date')

                SentSms.objects.create(**r).save()

        except (APIException, HTTPException) as e:
            return self.internal_error(message=[8, str(e)])

        return self.success(data=res, message=[7])


class SMSStatus(ViewTemplate):

    @ViewTemplate.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        """sms-status

        https://kavenegar.com/rest.html#sms-status
        https://kavenegar.com/rest.html#sms-statuslocalmessageid
        """

        data = self.request.query_params
        api = KavenegarAPI(self._sms_api_key)
        try:
            res = api.sms_status(data) if data['messageid'] else api.sms_statuslocalmessageid(data)
        except (APIException, HTTPException) as e:
            return self.internal_error(message=[9, str(e)])

        return self.success(data=res)


class SelectSMS(ViewTemplate):
    #  BUG  need an ip to be set
    @ViewTemplate.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        """sms-select

        https://kavenegar.com/rest.html#sms-select
        https://kavenegar.com/rest.html#sms-selectlatest
        """

        data = self.request.query_params
        api = KavenegarAPI(self._sms_api_key)
        try:
            res = api.sms_select(data) if 'messageid' in data else api.sms_latestoutbox(data)
            print(res)
        except (APIException, HTTPException) as e:
            return self.internal_error(message=[9, str(e)])

        return self.success(data=res)


class CancelSms(ViewTemplate):

    @ViewTemplate.generic_decor()
    @JsonValidation.validate
    def delete(self, request):
        """sms-cancel

        https://kavenegar.com/rest.html#sms-cancel
        """

        data = self.request.query_params
        api = KavenegarAPI(self._sms_api_key)

        try:
            res = api.sms_cancel(data)
        except (APIException, HTTPException) as e:
            return self.internal_error(message=[10, str(e)])

        return self.success(data=res, message=[11])


class SelectOutBoxSMS(ViewTemplate):
    # BUG bc of wrong timestamp format(unix time)
    @ViewTemplate.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        """sms-selectoutbox

        https://kavenegar.com/rest.html#sms-selectoutbox
        """

        data = self.request.query_params
        api = KavenegarAPI(self._sms_api_key)
        try:
            res = api.sms_selectoutbox(data)
        except (APIException, HTTPException) as e:
            return self.internal_error(message=[Helpers.kr_error_code(str(e))])  # nazaret?
            # return self.internal_error(message=[9, str(e)])

        return self.success(data=res)


class CountOutBoxSMS(ViewTemplate):
    # BUG bc of wrong timestamp format(unix time)
    @ViewTemplate.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        """sms-countoutbox

        https://kavenegar.com/rest.html#sms-countoutbox
        """

        data = self.request.query_params
        api = KavenegarAPI(self._sms_api_key)
        try:
            res = api.sms_countoutbox(data)
        except (APIException, HTTPException) as e:
            return self.internal_error(message=[9, str(e)])

        return self.success(data=res)


class CountInBoxSMS(ViewTemplate):
    # BUG bc of wrong timestamp format(unix time)
    @ViewTemplate.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        """sms-countinbox

        https://kavenegar.com/rest.html#sms-countinbox
        """

        data = self.request.query_params
        api = KavenegarAPI(self._sms_api_key)

        try:
            res = api.sms_countinbox(data)
        except (APIException, HTTPException) as e:
            return self.internal_error(message=[9, str(e)])

        return self.success(data=res)


class ReadInbox(ViewTemplate):
    @ViewTemplate.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        """sms-unreads

        https://kavenegar.com/rest.html#sms-unreads
        """

        data = self.request.query_params
        api = KavenegarAPI(self._sms_api_key)
        try:
            res = api.sms_receive(data)
        except (APIException, HTTPException) as e:
            return self.internal_error(message=[9, str(e)])

        return self.success(data=res)
