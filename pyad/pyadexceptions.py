class BaseException(Exception):
    pass


class comException(BaseException):
    def __init__(self, error_info, additional_info={}):
        self.error_info = error_info
        self.additional_info = additional_info

    def __str__(self):
        return "%s (%s): %s" % (
            str(self.error_info["error_constant"]),
            str(self.error_info["error_code"]),
            str(self.error_info["error_message"]),
        )


class genericADSIException(comException):
    def __str__(self):
        return "%s (%s): %s" % (
            self.error_info["error_constant"],
            self.error_info["error_code"],
            self.error_info["error_message"],
        )


class win32Exception(comException):
    def __str__(self):
        return "%s: %s" % (self.error_info["error_code"], self.error_info["message"])


class invalidOwnerException(BaseException):
    def __str__(self):
        return "The submitted object is not eligible to own another object."


class noObjectFoundException(BaseException):
    def __str__(self):
        return "The requested object does not exist."


class InvalidObjectException(noObjectFoundException, win32Exception):
    pass


class InvalidAttribute(BaseException, AttributeError):
    def __str__(self):
        return (
            'The attribute "%s" is not permitted by the schema definition of the '
            'object "%s" (the requested attribute does not exist).'
            % (self.attribute, self.obj)
        )


class noExecutedQuery(BaseException):
    def __str__(self):
        return (
            "No query has been executed. Therefore there are no results to return. "
            "Execute a query before requesting results."
        )


class invalidResults(BaseException):
    def __init__(self, numberResults):
        self.number_results = numberResults

    def __str__(self):
        return (
            "The specified query returned %i results. getSingleResults only functions "
            "with a single result." % self.number_results
        )


class SetupError(BaseException):
    pass
