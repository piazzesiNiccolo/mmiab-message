import string
import os
from flask import current_app as app


class ContentFilter:
    __UNSAFE_WORDS = []
    __alphanumeric = string.ascii_letters + string.digits

    @staticmethod
    def unsafe_words():
        """
        Populates unsafe_words list with the contents of a file in monolith/static/txt folder
        if the list is still empty.
        Returns the unsafe words list.
        """
        if len(ContentFilter.__UNSAFE_WORDS) == 0:

            with open(
                os.path.join(app.config["UNSAFE_WORDS_FOLDER"], "unsafe_words.txt"), "r"
            ) as f:
                lines = f.readlines()

            for l in lines:
                ContentFilter.__UNSAFE_WORDS.append(l.strip())

        return ContentFilter.__UNSAFE_WORDS

    @staticmethod
    def filter_content(message_body) -> bool:
        """
        For every word in the message_body string checks if it is unsafe.
        For every occurrence of the unsafe words in the body it is checked that
        it is followed and preceded by non-alphanumeric characters.
        It at least an unsafe word was found returns True, False otherwise.
        """
        _body = message_body.lower()
        _unsafe_words = ContentFilter.unsafe_words()
        for uw in _unsafe_words:
            index = _body.find(uw)
            while index >= 0:
                if (
                    (index > 0 and _body[index - 1] not in ContentFilter.__alphanumeric)
                    or index == 0
                ) and (
                    (
                        index + len(uw) < len(_body)
                        and _body[index + len(uw)] not in ContentFilter.__alphanumeric
                    )
                    or index + len(uw) == len(_body)
                ):
                    return True

                index = _body.find(uw, index + 1)

        return False
