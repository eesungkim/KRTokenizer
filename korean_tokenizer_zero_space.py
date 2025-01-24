class HangulSplitterCombiner:
    _FINAL_JAMO = [
        None,  # 0 -> no final consonant
        'ㄱ',  # 1
        'ㄲ',  # 2
        'ㄳ',  # 3
        'ㄴ',  # 4
        'ㄵ',  # 5
        'ㄶ',  # 6
        'ㄷ',  # 7
        'ㄹ',  # 8
        'ㄺ',  # 9
        'ㄻ',  # 10
        'ㄼ',  # 11
        'ㄽ',  # 12
        'ㄾ',  # 13
        'ㄿ',  # 14
        'ㅀ',  # 15
        'ㅁ',  # 16
        'ㅂ',  # 17
        'ㅄ',  # 18
        'ㅅ',  # 19
        'ㅆ',  # 20
        'ㅇ',  # 21
        'ㅈ',  # 22
        'ㅊ',  # 23
        'ㅋ',  # 24
        'ㅌ',  # 25
        'ㅍ',  # 26
        'ㅎ'   # 27
    ]

    _FINAL_JAMO_TO_INDEX = {
        'ㄱ':1, 'ㄲ':2, 'ㄳ':3, 'ㄴ':4, 'ㄵ':5, 'ㄶ':6,
        'ㄷ':7, 'ㄹ':8, 'ㄺ':9, 'ㄻ':10, 'ㄼ':11, 'ㄽ':12,
        'ㄾ':13, 'ㄿ':14, 'ㅀ':15, 'ㅁ':16, 'ㅂ':17, 'ㅄ':18,
        'ㅅ':19, 'ㅆ':20, 'ㅇ':21, 'ㅈ':22, 'ㅊ':23, 'ㅋ':24,
        'ㅌ':25, 'ㅍ':26, 'ㅎ':27
    }

    @staticmethod
    def _decompose_syllable(syllable: str):
        """
        Return (initial_idx, medial_idx, final_idx) for a standard Hangul syllable (가~힣).
        If it's out of range, return None.
        """
        code = ord(syllable)
        if code < 0xAC00 or code > 0xD7A3:
            return None
        offset = code - 0xAC00
        i_idx = offset // (21 * 28)
        m_idx = (offset % (21 * 28)) // 28
        f_idx = (offset % (21 * 28)) % 28
        return (i_idx, m_idx, f_idx)

    @staticmethod
    def _compose_syllable(i_idx: int, m_idx: int, f_idx: int) -> str:
        """
        Compose a syllable from initial, medial, final indices.
        (초성, 중성, 종성) -> "가~힣"
        """
        code = 0xAC00 + (i_idx * 21 * 28) + (m_idx * 28) + f_idx
        return chr(code)

    def decompose(self, text: str) -> str:
        """
        For each Hangul syllable in `text`, separate it into:
         - one block containing (초성 + 중성) with 종성=0
         - followed by a zero-width space (U+200B) 
           and a separate jamo character if 종성 != 0

        e.g. "실행" -> "시\u200Bㄹ해\u200Bㅇ"
        """
        ZWS = "\u200B"  # zero-width space
        result = []

        for char in text:
            # Decompose if it's within Hangul range
            imf = self._decompose_syllable(char)
            if imf is None:
                # Not a Hangul syllable in range, just append it
                result.append(char)
                continue

            i_idx, m_idx, f_idx = imf
            # Rebuild the (initial+medial) only
            im_char = self._compose_syllable(i_idx, m_idx, 0)
            result.append(im_char)

            # If there's a final consonant, insert zero-width space + jamo
            if f_idx != 0:
                final_jamo = self._FINAL_JAMO[f_idx]
                if final_jamo:
                    result.append(ZWS)
                    result.append(final_jamo)

        return "".join(result)

    def compose(self, text: str) -> str:
        """
        Reverse of `decompose`. Given text where each original syllable is
        split into "initial+medial block" + optional "final jamo":

        e.g. "시\u200Bㄹ해\u200Bㅇ" -> "실행"
        """
        result = []
        i = 0
        length = len(text)

        while i < length:
            c = text[i]
            code = ord(c)

            # If not a Hangul block, just append
            if code < 0xAC00 or code > 0xD7A3:
                result.append(c)
                i += 1
                continue

            # We assume this char is "initial+medial" (with final=0)
            imf = self._decompose_syllable(c)
            if imf is None:
                # fallback
                result.append(c)
                i += 1
                continue

            i_idx, m_idx, f_idx = imf
            # Check if next char is a valid final jamo 
            # (possibly preceded by a zero-width space)
            # We'll skip \u200B if present
            peek_idx = i + 1

            # If there's a zero-width space next, skip it
            if peek_idx < length and text[peek_idx] == "\u200B":
                peek_idx += 1

            if peek_idx < length:
                next_char = text[peek_idx]
                if next_char in self._FINAL_JAMO_TO_INDEX:
                    # We have a final consonant
                    f_idx = self._FINAL_JAMO_TO_INDEX[next_char]
                    i = peek_idx + 1  # move past final jamo
                    result.append(self._compose_syllable(i_idx, m_idx, f_idx))
                    continue

            # Otherwise, no final or not a valid final
            result.append(self._compose_syllable(i_idx, m_idx, 0))
            i += 1

        return "".join(result)

