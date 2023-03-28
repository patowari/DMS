#!/usr/bin/env python

import doctest
import re
import sys

VERSION_PART_MAJOR = 0
VERSION_PART_MINOR = 1
VERSION_PART_MICRO = 2
VERSION_PART_LOCAL = 3


class Version:
    """
    # Return value

    >>> Version('1')
    Version: 1
    >>> Version('1.0')
    Version: 1.0
    >>> Version('1.3.2')
    Version: 1.3.2
    >>> Version('1.3.2+local.1')
    Version: 1.3.2+local.1

    # Increment part

    >>> Version('1').increment_part(part=VERSION_PART_MAJOR)
    Version: 2
    >>> Version('1').increment_part(part=VERSION_PART_MINOR)
    Version: 1.1
    >>> Version('1').increment_part(part=VERSION_PART_MICRO)
    Version: 1.0.1
    >>> Version('1rc').increment_part(part=VERSION_PART_MAJOR)
    Version: 2rc
    >>> Version('1rc2').increment_part(part=VERSION_PART_MAJOR)
    Version: 1rc3
    >>> Version('1rc0').increment_part(part=VERSION_PART_MAJOR)
    Version: 1rc1
    >>> Version('1.rc0').increment_part(part=VERSION_PART_MINOR)
    Version: 1.rc1
    >>> Version('1.0.rc1').increment_part(part=VERSION_PART_MINOR)
    Version: 1.1
    >>> Version('1.0.rc1').increment_part(part=VERSION_PART_MICRO)
    Version: 1.0.rc2
    >>> Version('1rc').increment_part(part=VERSION_PART_MINOR)
    Version: 1rc.1
    >>> Version('1rc').increment_part(part=VERSION_PART_MINOR)
    Version: 1rc.1
    >>> Version('1rc').increment_part(part=VERSION_PART_MICRO)
    Version: 1rc.0.1
    >>> Version('1.rc1').increment_part(part=VERSION_PART_MINOR)
    Version: 1.rc2
    >>> Version('1.rc1').increment_part(part=VERSION_PART_MICRO)
    Version: 1.rc1.1
    >>> Version('1.1.rc1').increment_part(part=VERSION_PART_MICRO)
    Version: 1.1.rc2
    >>> Version('1.2.3').increment_major()
    Version: 2
    >>> Version('1.2.3').increment_minor()
    Version: 1.3
    >>> Version('1.2.3').increment_micro()
    Version: 1.2.4

    # Increment part, local version

    >>> Version('1.2.3+local.1').increment_major()
    Version: 2+local.1
    >>> Version('1.2.3+local.1').increment_minor()
    Version: 1.3+local.1
    >>> Version('1.2.3+local.1').increment_micro()
    Version: 1.2.4+local.1

    # As a part

    >>> Version('1.2.3').as_major()
    '1'
    >>> Version('1.2.3').as_minor()
    '1.2'
    >>> Version('1.2.3').as_micro()
    '1.2.3'
    >>> Version('1.2').as_micro()
    ''

    # As a part, local version

    >>> Version('1.2.3+local.1').as_major()
    '1+local.1'
    >>> Version('1.2.3+local.1').as_minor()
    '1.2+local.1'
    >>> Version('1.2.3+local.1').as_micro()
    '1.2.3+local.1'
    >>> Version('1.2+local.1').as_micro()
    ''
    >>> Version('1+local.1').as_minor()
    ''

    # As a part, local version, as upstream

    >>> Version('1+local.1').as_upstream()
    '1'
    >>> Version('1.2+local.1').as_upstream()
    '1.2'
    >>> Version('1.2.3+local.1').as_upstream()
    '1.2.3'

    # Comparison, greater than

    >>> Version('1') > Version('2')
    False
    >>> Version('2') > Version('1')
    True
    >>> Version('1.1') > Version('1.2')
    False
    >>> Version('1.2') > Version('1.1')
    True
    >>> Version('1.1.2') > Version('1.1.1')
    True
    >>> Version('1.1.1') > Version('1.1.2')
    False
    >>> Version('1.1') > Version('2')
    False
    >>> Version('1.1') > Version('1')
    True
    >>> Version('1') > Version('1.1')
    False

    # Comparison, greater than, different local, same upstream

    >>> Version('1') > Version('1+local.1')
    False
    >>> Version('1+local.1') > Version('1')
    True
    >>> Version('1.2') > Version('1.2+local.1')
    False
    >>> Version('1.2+local.1') > Version('1.2')
    True
    >>> Version('1.1.1') > Version('1.1.1+local.1')
    False
    >>> Version('1.1.1+local.1') > Version('1.1.1')
    True

    # Comparison, greater than, same local, different upstream

    >>> Version('1+local.1') > Version('2+local.1')
    False
    >>> Version('2+local.1') > Version('1+local.1')
    True
    >>> Version('1.1+local.1') > Version('1.2+local.1')
    False
    >>> Version('1.2+local.1') > Version('1.1+local.1')
    True
    >>> Version('1.1.1+local.1') > Version('1.1.2+local.1')
    False
    >>> Version('1.1.2+local.1') > Version('1.1.1+local.1')
    True

    # Comparison, greater than, different local, different upstream

    >>> Version('1+local.1') > Version('2')
    False
    >>> Version('2') > Version('1+local.1')
    True
    >>> Version('1+local.1') > Version('1.2')
    False
    >>> Version('1.1') > Version('1+local.1')
    True
    >>> Version('1+local.1') > Version('1.1')
    False
    >>> Version('1.2') > Version('1+local.1')
    True
    >>> Version('1+local.1') > Version('1.2')
    False
    >>> Version('1.1+local.1') > Version('1.2')
    False
    >>> Version('1.2') > Version('1.1+local.1')
    True
    >>> Version('1.1.1+local.1') > Version('1.1.2')
    False
    >>> Version('1.1.2') > Version('1.1.1+local.1')
    True
    >>> Version('1.1.2+local.1') > Version('1.1.1')
    True
    >>> Version('1.1.1') > Version('1.1.2+local.1')
    False

    # Comparison, less than

    >>> Version('1') < Version('2')
    True
    >>> Version('2') < Version('1')
    False
    >>> Version('1.1') < Version('1.2')
    True
    >>> Version('1.2') < Version('1.1')
    False
    >>> Version('1.1.2') < Version('1.1.1')
    False
    >>> Version('1.1.1') < Version('1.1.2')
    True
    >>> Version('1.1') < Version('2')
    True
    >>> Version('1.1') < Version('1')
    False
    >>> Version('1') < Version('1.1')
    True

    # Comparison, greater than, different local, same upstream

    >>> Version('1') < Version('1+local.1')
    True
    >>> Version('1+local.1') < Version('1')
    False
    >>> Version('1.2') < Version('1.2+local.1')
    True
    >>> Version('1.2+local.1') < Version('1.2')
    False
    >>> Version('1.1.1') < Version('1.1.1+local.1')
    True
    >>> Version('1.1.1+local.1') < Version('1.1.1')
    False

    # Comparison, greater than, same local, different upstream

    >>> Version('1+local.1') < Version('2+local.1')
    True
    >>> Version('2+local.1') < Version('1+local.1')
    False
    >>> Version('1.1+local.1') < Version('1.2+local.1')
    True
    >>> Version('1.2+local.1') < Version('1.1+local.1')
    False
    >>> Version('1.1.1+local.1') < Version('1.1.2+local.1')
    True
    >>> Version('1.1.2+local.1') < Version('1.1.1+local.1')
    False

    # Comparison, greater than, different local, different upstream

    >>> Version('1+local.1') < Version('2')
    True
    >>> Version('2') < Version('1+local.1')
    False
    >>> Version('1+local.1') < Version('1.2')
    True
    >>> Version('1.1') < Version('1+local.1')
    False
    >>> Version('1+local.1') < Version('1.1')
    True
    >>> Version('1.2') < Version('1+local.1')
    False
    >>> Version('1+local.1') < Version('1.2')
    True
    >>> Version('1.1+local.1') < Version('1.2')
    True
    >>> Version('1.2') < Version('1.1+local.1')
    False
    >>> Version('1.1.1+local.1') < Version('1.1.2')
    True
    >>> Version('1.1.2') < Version('1.1.1+local.1')
    False
    >>> Version('1.1.2+local.1') < Version('1.1.1')
    False
    >>> Version('1.1.1') < Version('1.1.2+local.1')
    True
    """
    def __eq__(self, other):
        return self.major == other.major and self.minor == other.minor and self.micro == other.micro

    def __gt__(self, other):
        if int(self.major or 0) != int(other.major or 0):
            return int(self.major or 0) > int(other.major or 0)

        if int(self.minor or 0) != int(other.minor or 0):
            return int(self.minor or 0) > int(other.minor or 0)

        if int(self.micro or 0) != int(other.micro or 0):
            return int(self.micro or 0) > int(other.micro or 0)

        if self.local and not other.local:
            return True
        else:
            return False

    def __lt__(self, other):
        if int(self.major or 0) != int(other.major or 0):
            return int(self.major or 0) < int(other.major or 0)

        if int(self.minor or 0) != int(other.minor or 0):
            return int(self.minor or 0) < int(other.minor or 0)

        if int(self.micro or 0) != int(other.micro or 0):
            return int(self.micro or 0) < int(other.micro or 0)

        if not self.local and other.local:
            return True
        else:
            return False

    def __init__(self, version_string):
        self._version_string = version_string
        self._version_parts = []
        self._version_parts_local = None

        part = []
        version_part_flag = True
        for character in self._version_string:
            if version_part_flag:
                if character == '+':
                    version_part_flag = False
                    self._version_parts.append(
                        ''.join(part)
                    )
                    part = []
                elif character != '.':
                    part.append(character)
                else:
                    self._version_parts.append(
                        ''.join(part)
                    )
                    part = []
            else:
                part.append(character)

        if version_part_flag:
            self._version_parts.append(
                ''.join(part)
            )
        else:
            self._version_parts_local = ''.join(part)

    def _get_version_part(self, index):
        if index == VERSION_PART_LOCAL:
            return self._version_parts_local
        else:
            try:
                return self._version_parts[index]
            except IndexError:
                return 0

    def __repr__(self):
        return 'Version: {}'.format(
            self.get_version_string()
        )

    def as_upstream(self):
        parts = [self.major]

        if self.minor:
            parts.append(self.minor)
        if self.micro:
            parts.append(self.micro)

        return '.'.join(parts)

    def as_major(self):
        result = self.major

        if self.local and result:
            result = '{}+{}'.format(result, self.local)

        return result

    def as_minor(self):
        result = ''

        if self.minor:
            result = '{}.{}'.format(self.major, self.minor)

        if self.local and result:
            result = '{}+{}'.format(result, self.local)

        return result

    def as_micro(self):
        result = ''
        if self.micro:
            result = '{}.{}.{}'.format(self.major, self.minor, self.micro)

        if self.local and result:
            result = '{}+{}'.format(result, self.local)

        return result

    def increment_major(self):
        return self.increment_part(part=VERSION_PART_MAJOR)

    def increment_minor(self):
        return self.increment_part(part=VERSION_PART_MINOR)

    def increment_micro(self):
        return self.increment_part(part=VERSION_PART_MICRO)

    def increment_part(self, part):
        # Fill version parts if the requested part is lower than what is
        # available.
        self._version_parts.extend(
            ['0'] * (
                part - len(self._version_parts) + 1
            )
        )

        try:
            version_part = self._version_parts[part]
        except IndexError:
            part_numeric_post = ''
            part_numeric_pre = ''
            part_text = ''
        else:
            part_numeric_pre, part_text, part_numeric_post = re.findall(
                r'^(\d+)*([A-Za-z]+)*(\d+)*$', version_part
            )[0]

        if part_numeric_post:
            part_numeric_post = int(part_numeric_post) + 1
        else:
            part_numeric_pre = int(part_numeric_pre) + 1

        self._version_parts[part] = '{}{}{}'.format(
            part_numeric_pre, part_text, part_numeric_post
        )

        # Discard version parts lower than what is being increased
        self._version_parts = self._version_parts[0:part + 1]
        self._version_string = '.'.join(self._version_parts)

        if self.local:
            self._version_string = '{}+{}'.format(
                self._version_string, self.local
            )

        return self

    def get_version_string(self):
        return self._version_string

    @property
    def local(self):
        return self._get_version_part(VERSION_PART_LOCAL)

    @property
    def major(self):
        return self._get_version_part(VERSION_PART_MAJOR)

    @property
    def minor(self):
        return self._get_version_part(VERSION_PART_MINOR)

    @property
    def micro(self):
        return self._get_version_part(VERSION_PART_MICRO)


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '-test':
        doctest.testmod()
        exit(0)

    if len(sys.argv) == 1:
        print(
            'usage: [version] <part to retrieve [major, minor, micro]> <-test>'
        )
        exit(0)

    if len(sys.argv) < 3:
        print('Insufficient arguments')
        exit(1)

    version_string = sys.argv[1]
    if version_string == '-':
        version_string = sys.stdin.read().replace('\n', '')

    version = Version(version_string=version_string)
    part = sys.argv[2].lower()

    if part == 'major':
        output = version.as_major()
    elif part == 'minor':
        output = version.as_minor() or ''
    elif part == 'micro':
        output = version.as_micro() or ''
    elif part == 'upstream':
        output = version.as_upstream() or ''
    else:
        print('Unknown part')
        exit(1)

    print(output)
