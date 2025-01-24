class HangulSplitterCombiner:
    """
    Decompose: 
      e.g. "실행" -> "ㅅㅣㄹㅎㅐㅇ"
    Compose: 
      e.g. "ㅅㅣㄹㅎㅐㅇ" -> "실행"
    """
    _INITIAL_COMPAT = [
        'ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ',
        'ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'
    ]

    _MEDIAL_COMPAT = [
        'ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ',
        'ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ',
        'ㅡ','ㅢ','ㅣ'
    ]

    _FINAL_COMPAT = [
        None, # 0 -> No 종성
        'ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ',
        'ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ',
        'ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'
    ]

    # Reverse dictionaries for compose()
    _INITIAL_MAP = { jamo:i for i,jamo in enumerate(_INITIAL_COMPAT) }
    _MEDIAL_MAP  = { jamo:i for i,jamo in enumerate(_MEDIAL_COMPAT) }
    # Final map starts from index 1
    _FINAL_MAP   = { jamo:i for i,jamo in enumerate(_FINAL_COMPAT) if jamo is not None }

    @staticmethod
    def _compose_syllable(i_idx: int, m_idx: int, f_idx: int) -> str:
        """
        Given indices for initial, medial, final,
        return the corresponding Hangul syllable (가~힣).
        """
        # Unicode Hangul block start
        base_code = 0xAC00
        code = base_code + (i_idx * 21 * 28) + (m_idx * 28) + f_idx
        return chr(code)

    def decompose(self, text: str) -> str:
        """
        For each Hangul syllable (가~힣), convert to up to 3 compatibility jamo:
          (초성 jamo) + (중성 jamo) + (optionally 종성 jamo)
        e.g. "실행" -> "ㅅㅣㄹㅎㅐㅇ"
        Non-Hangul chars are returned unchanged.
        """
        result = []

        for ch in text:
            code = ord(ch)
            # Check if it's in Hangul Syllable range
            if code < 0xAC00 or code > 0xD7A3:
                # Just append as-is
                result.append(ch)
                continue

            # Decompose to i_idx, m_idx, f_idx
            offset = code - 0xAC00
            i_idx = offset // (21 * 28)
            m_idx = (offset % (21 * 28)) // 28
            f_idx = (offset % (21 * 28)) % 28

            # Map to compatibility jamo
            initial_jamo = self._INITIAL_COMPAT[i_idx]
            medial_jamo  = self._MEDIAL_COMPAT[m_idx]
            result.append(initial_jamo)
            result.append(medial_jamo)

            if f_idx != 0:
                final_jamo = self._FINAL_COMPAT[f_idx]
                if final_jamo:
                    result.append(final_jamo)

        return "".join(result)

    def compose(self, decomposed_text: str) -> str:
        """
        Rebuild Hangul syllables from a string of compatibility jamo.
        Looks for a sequence:
           (initial jamo) + (medial jamo) [+ (final jamo)]
        e.g. "ㅅㅣㄹㅎㅐㅇ" -> "실행"
        Non-jamo or out-of-order chars are copied as-is.
        """
        result = []
        i = 0
        n = len(decomposed_text)

        while i < n:
            c = decomposed_text[i]

            # 1) Check if 'c' is an initial jamo
            if c in self._INITIAL_MAP and (i + 1) < n:
                # 2) Check next char for a medial jamo
                c2 = decomposed_text[i+1]
                if c2 in self._MEDIAL_MAP:
                    # We have initial + medial
                    i_idx = self._INITIAL_MAP[c]
                    m_idx = self._MEDIAL_MAP[c2]
                    i += 2
                    f_idx = 0

                    # 3) Check if there's a final jamo
                    if i < n:
                        c3 = decomposed_text[i]
                        if c3 in self._FINAL_MAP:
                            f_idx = self._FINAL_MAP[c3]
                            i += 1

                    # Now compose the block
                    block = self._compose_syllable(i_idx, m_idx, f_idx)
                    result.append(block)
                    continue
                # else: not a valid medial, so just append 'c' and move on
            # Not a recognized pattern => copy char
            result.append(c)
            i += 1

        return "".join(result)

