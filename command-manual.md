# LUNA-U Hardware Command Manual

**Unified audio matrix processor**

audac.eu/eu/products/d/LUNA-U/command-manual HARDWARE
            COMMAND MANUAL

# LUNA-U

## Unified audio
            matrix processor

### Table
            of contents

Luna-U Commands List - V1.5 Luna-U Commands List - V1.6

#### Luna-U
            Commands List - V1.5

## Port
            Numbers

| ‌ Protocol | Port
                        Number | Number
                        of Available Sockets |
| --- | --- | --- |
| TCP | 5001 | 10 |
| UDP | 8711 | - |
| Websocket | 80 | 50 |

## Uart
            Information

| Baud
                        rate | 19200 |
| --- | --- |
| Data
                        bits | 8 |
| Start
                        bit | 1 |
| Stop
                        bit | 1 |
| Parity | None |

# ASCII
            Commands (Luna U)

Version:
            1.5.0

This is
            the list of ASCII Commands supported by this device. An ASCII
            command always follows the same structure:

#|Destination|Source|Type^Target^Command|Arguments|CRC|CRLF

This
            format uses 3 separator characters for different levels of
            separating each value in the message:

Message
            separator '|':

This
            separates a message in 7 blocks (if you include the start
            '#' and end <CRLF>)

Block
            separator '^':

This
            splits a block into logical elements. This is used to split the
            command in the message type, 'command' and
            'target'

Value
            separator '>':

This
            splits up a logical single value in their primitives, for example: a
            target consists of a channel type and a channel index, split by
            '>'

### Messages
            are Case sensitive, if the example shows the text in uppercase, this
            should always be uppercase!

## Destination

The
            target device. This consists of 2 parts: Device>Address .

### Device

This
            is the device type: LUNA_U Address

This
            is the user configurable device address, default: 1 . You can
            also leave this field empty, this results in all Luna U devices that
            receive this command to respond.

| Examples | Destination |
| --- | --- |
| default
                        destination | LUNA_U>1 |
| broadcast
                        to all Luna U devices | LUNA_U |

### Device
            Matching

If the
            device type or address does not match, the message will be ignored.
            Device Address 0 is a special address and will always match (this
            can be seen as a broadcast)

| Destination | Device
                        address: LUNA_U>2 | Remarks |
| --- | --- | --- |
| LUNA_U>2 | Destination
                        Matches Device | this
                        is an exact match |
| LUNA_U>1 | Message
                        ignored | the
                        destination address does not match |
| LUNA_U | Destination
                        Matches Device | the
                        destination address will always match |
| LUNA_U>0 | Destination
                        Matches Device | Equivalent
                        to LUNA_U |
| CLIENT>2 | Message
                        ignored | the
                        device type does not match |
| CLIENT | Message
                        ignored | the
                        device type does not match |

## Source
            (optional)

The
            source address is optional when sending, but the device will always
            fill this field with its own address.

| Examples | Sent
                        message | Response
                        message LUNA_U>2 |
| --- | --- | --- |
| broadcast
                        to a Luna U | #|LUNA_U||...|<CRLF> | #||LUNA_U>2|...|<CRLF> |
| send
                        to a specific Luna U | #|LUNA_U>2||...|<CRLF> | #||LUNA_U>2|...|<CRLF> |
| use
                        a source address in the request message | #|LUNA_U|CLIENT>1|...|<CRLF> | #|CLIENT>1|LUNA_U>2|...|<CRLF> |

## Type

The
            type explains what the message wants to do. There are 3 supported
            message types:

| Type | From | To | Explanation |
| --- | --- | --- | --- |
| SET_REQ | CLIENT | Luna
                        U | Change
                        a setting in the Luna U |
| GET_REQ | CLIENT | Luna
                        U | Request
                        the current status of a setting in the Luna
                        U |
| GET_RSP | Luna
                        U | CLIENT | Response
                        to either a GET_REQ or SET_REQ, if the request was
                        valid |

## Command,
            Target, Arguments

These
            3 parameters are explained together, because they influence each
            other. The command dictates the meaning of the argument, while the
            target distinguishes which exact setting you want to change. the
            target can also influence the valid range of the argument.

Some
            commands (like the mixer) can have a range arguments (for the mixer:
            all mixer volumes are an individual argument). In this case, the
            argument looks like:

idx>val[^idx2>val2] , where the part in between the brackets [] can appear 0 or more times.

idx,
            ídx2, ...: the argument index

val,
            val2, ...: the value at the specified index

This
            device supports special ALL_* commands that
            allow you to set multiple values in a single command. They look
            similar to their single counterparts, but the Target

starts
            with ALL_ . The Argument is an array
            of elements, separated by "block separators", instead of a
            single value. For example: if there's a device that supports
            grouping 2 MUTE commands, the following can be shortened:

#|LUNA_U>1||SET_REQ^TARGET>1^MUTE|TRUE|U|<CRLF>
            #|LUNA_U>1||SET_REQ^TARGET>2^MUTE|TRUE|U|<CRLF>

becomes

#|LUNA_U>1||SET_REQ^ALL_TARGET^MUTE|TRUE^TRUE|U|<CRLF>

Note:
            For backwards compatibility reasons there might be gaps in the
            arguments sent, it is important to leave these gaps in the command
            you build! A gap is created by putting 2 block separators next to
            each other: "^^".

You
            can leverage this as well, if there are parts of this grouped
            command you don't want to change. You can then leave this value
            empty like the gaps, and you can only change the values you want,
            leaving the rest as is.

TRUE^^FALSE : Set the first value to true, leave the second value
                as is, set the third value to false.

You
            can also skip the last elements in the list, if you don't want
            to change them. For example: the command groups 4 volumes together,
            all. If you only want to change the first two values, you have 2
            options for the "Arguments" field:

-15^-30^^

-15^-30

Both
            are equivalent, but in the first example you explicitly define the
            third and fourth values as "gaps", in the second example
            they are implicitly defined as gaps.

### APPLY_SNAPSHOT

applies
            a snapshot

### Argument
            (id) : the name of the snapshot to
                apply

| Target | Argument | Example
                        (default value) |
| --- | --- | --- |
| SNAPSHOTS>1 | regex:
                        ^(settings\/snapshots\/)[a-zA-Z0-9
                        _-]+\.snapshot$ | #|LUNA_U>1||SET_REQ^SNAPSHOTS>1^APPLY_SNAPSHOT|settings/snapshots/New
                        Snapshot.snapshot|U|<CRLF> |

### VOLUME

Set a
            single Volume in dB

### Argument
            (volume) : the requested Volume in
                dB

| Target | Argument | Example
                        (default value) |
| --- | --- | --- |
| INPUT_LINE>1>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_LINE>1>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_LINE>2>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_LINE>2>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_LINE>3>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_LINE>3>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_LINE>4>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_LINE>4>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_LINE>5>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_LINE>5>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_LINE>6>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_LINE>6>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_LINE>7>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_LINE>7>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_LINE>8>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_LINE>8>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_LINE>9>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_LINE>9>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_LINE>10>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_LINE>10>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_LINE>11>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_LINE>11>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_LINE>12>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_LINE>12>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>1>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>1>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>2>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>2>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>3>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>3>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>4>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>4>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>5>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>5>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>6>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>6>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>7>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>7>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>8>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>8>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>9>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>9>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>10>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>10>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>11>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>11>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>12>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>12>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>13>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>13>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>14>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>14>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>15>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>15>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>16>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>16>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>17>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>17>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>18>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>18>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>19>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>19>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>20>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>20>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>21>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>21>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>22>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>22>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>23>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>23>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>24>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>24>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>25>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>25>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>26>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>26>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>27>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>27>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>28>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>28>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>29>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>29>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_DANTE>30>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>30>VOLUME>1^VOLUME|0|U|<CRLF> |

| INPUT_DANTE>31>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>31>VOLUME>1^VOLUME|0|U|<CRLF> |
| --- | --- | --- |
| INPUT_DANTE>32>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>32>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_OS>1>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_OS>1>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_OS>2>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_OS>2>VOLUME>1^VOLUME|0|U|<CRLF> |
| INPUT_GENERATOR>1>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^INPUT_GENERATOR>1>VOLUME>1^VOLUME|0|U|<CRLF> |
| ZONE>1>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>1>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>2>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>2>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>3>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>3>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>4>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>4>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>5>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>5>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>6>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>6>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>7>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>7>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>8>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>8>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>9>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>9>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>10>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>10>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>11>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>11>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>12>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>12>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>13>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>13>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>14>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>14>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>15>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>15>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>16>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>16>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>17>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>17>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>18>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>18>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>19>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>19>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>20>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>20>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>21>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>21>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>22>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>22>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>23>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>23>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>24>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>24>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>25>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>25>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>26>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>26>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>27>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>27>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>28>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>28>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>29>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>29>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>30>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>30>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>31>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>31>VOLUME>1^VOLUME|-90|U|<CRLF> |
| ZONE>32>VOLUME>1 | min:
                        -90, max: 0 | #|LUNA_U>1||SET_REQ^ZONE>32>VOLUME>1^VOLUME|-90|U|<CRLF> |

#### Grouped
            Commands

### ALL_ZONES

example
            (default value):

#|LUNA_U>1||SET_REQ^ALL_ZONES^VOLUME|-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^

-90^-90^-90^-90^-90^-90^-90^-90^-90|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | ZONE>1>VOLUME>1 |
| 2 | ZONE>2>VOLUME>1 |
| 3 | ZONE>3>VOLUME>1 |
| 4 | ZONE>4>VOLUME>1 |
| 5 | ZONE>5>VOLUME>1 |
| 6 | ZONE>6>VOLUME>1 |
| 7 | ZONE>7>VOLUME>1 |
| 8 | ZONE>8>VOLUME>1 |
| 9 | ZONE>9>VOLUME>1 |
| 10 | ZONE>10>VOLUME>1 |
| 11 | ZONE>11>VOLUME>1 |
| 12 | ZONE>12>VOLUME>1 |
| 13 | ZONE>13>VOLUME>1 |
| 14 | ZONE>14>VOLUME>1 |
| 15 | ZONE>15>VOLUME>1 |
| 16 | ZONE>16>VOLUME>1 |
| 17 | ZONE>17>VOLUME>1 |
| 18 | ZONE>18>VOLUME>1 |
| 19 | ZONE>19>VOLUME>1 |
| 20 | ZONE>20>VOLUME>1 |
| 21 | ZONE>21>VOLUME>1 |
| 22 | ZONE>22>VOLUME>1 |
| 23 | ZONE>23>VOLUME>1 |
| 24 | ZONE>24>VOLUME>1 |
| 25 | ZONE>25>VOLUME>1 |
| 26 | ZONE>26>VOLUME>1 |
| 27 | ZONE>27>VOLUME>1 |
| 28 | ZONE>28>VOLUME>1 |
| 29 | ZONE>29>VOLUME>1 |
| 30 | ZONE>30>VOLUME>1 |
| 31 | ZONE>31>VOLUME>1 |
| 32 | ZONE>32>VOLUME>1 |

### ALL_DANTE_IN

example
            (default value): #|LUNA_U>1||SET_REQ^ALL_DANTE_IN^VOLUME|0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0|U|

<CRLF>

| Index | Target |
| --- | --- |
| 1 | INPUT_DANTE>1>VOLUME>1 |
| 2 | INPUT_DANTE>2>VOLUME>1 |
| 3 | INPUT_DANTE>3>VOLUME>1 |
| 4 | INPUT_DANTE>4>VOLUME>1 |
| 5 | INPUT_DANTE>5>VOLUME>1 |
| 6 | INPUT_DANTE>6>VOLUME>1 |
| 7 | INPUT_DANTE>7>VOLUME>1 |
| 8 | INPUT_DANTE>8>VOLUME>1 |
| 9 | INPUT_DANTE>9>VOLUME>1 |
| 10 | INPUT_DANTE>10>VOLUME>1 |
| 11 | INPUT_DANTE>11>VOLUME>1 |
| 12 | INPUT_DANTE>12>VOLUME>1 |
| 13 | INPUT_DANTE>13>VOLUME>1 |
| 14 | INPUT_DANTE>14>VOLUME>1 |
| 15 | INPUT_DANTE>15>VOLUME>1 |
| 16 | INPUT_DANTE>16>VOLUME>1 |
| 17 | INPUT_DANTE>17>VOLUME>1 |
| 18 | INPUT_DANTE>18>VOLUME>1 |
| 19 | INPUT_DANTE>19>VOLUME>1 |
| 20 | INPUT_DANTE>20>VOLUME>1 |
| 21 | INPUT_DANTE>21>VOLUME>1 |
| 22 | INPUT_DANTE>22>VOLUME>1 |
| 23 | INPUT_DANTE>23>VOLUME>1 |
| 24 | INPUT_DANTE>24>VOLUME>1 |
| 25 | INPUT_DANTE>25>VOLUME>1 |
| 26 | INPUT_DANTE>26>VOLUME>1 |
| 27 | INPUT_DANTE>27>VOLUME>1 |
| 28 | INPUT_DANTE>28>VOLUME>1 |
| 29 | INPUT_DANTE>29>VOLUME>1 |
| 30 | INPUT_DANTE>30>VOLUME>1 |
| 31 | INPUT_DANTE>31>VOLUME>1 |
| 32 | INPUT_DANTE>32>VOLUME>1 |

### ALL_ANALOG_IN

example
            (default value): #|LUNA_U>1||SET_REQ^ALL_ANALOG_IN^VOLUME|0^0^0^0^0^0^0^0^0^0^0^0|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | INPUT_LINE>1>VOLUME>1 |
| 2 | INPUT_LINE>2>VOLUME>1 |
| 3 | INPUT_LINE>3>VOLUME>1 |
| 4 | INPUT_LINE>4>VOLUME>1 |
| 5 | INPUT_LINE>5>VOLUME>1 |
| 6 | INPUT_LINE>6>VOLUME>1 |
| 7 | INPUT_LINE>7>VOLUME>1 |
| 8 | INPUT_LINE>8>VOLUME>1 |
| 9 | INPUT_LINE>9>VOLUME>1 |
| 10 | INPUT_LINE>10>VOLUME>1 |
| 11 | INPUT_LINE>11>VOLUME>1 |
| 12 | INPUT_LINE>12>VOLUME>1 |

### ALL_OS_IN

example
            (default value): #|LUNA_U>1||SET_REQ^ALL_OS_IN^VOLUME|0^0^0|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | INPUT_GENERATOR>1>VOLUME>1 |
| 2 | INPUT_OS>1>VOLUME>1 |
| 3 | INPUT_OS>2>VOLUME>1 |

### MUTE

mute an
            audio channel

### Argument
            (enabled) : is the audio channel
                muted

| Target | Argument | Example
                        (default value) |
| --- | --- | --- |
| INPUT_LINE>1>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_LINE>1>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_LINE>2>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_LINE>2>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_LINE>3>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_LINE>3>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_LINE>4>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_LINE>4>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_LINE>5>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_LINE>5>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_LINE>6>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_LINE>6>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_LINE>7>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_LINE>7>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_LINE>8>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_LINE>8>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_LINE>9>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_LINE>9>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_LINE>10>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_LINE>10>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_LINE>11>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_LINE>11>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_LINE>12>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_LINE>12>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>1>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>1>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>2>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>2>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>3>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>3>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>4>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>4>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>5>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>5>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>6>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>6>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>7>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>7>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>8>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>8>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>9>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>9>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>10>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>10>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>11>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>11>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>12>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>12>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>13>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>13>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>14>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>14>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>15>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>15>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>16>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>16>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>17>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>17>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>18>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>18>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>19>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>19>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>20>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>20>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>21>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>21>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>22>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>22>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>23>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>23>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>24>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>24>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>25>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>25>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>26>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>26>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>27>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>27>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>28>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>28>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>29>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>29>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_DANTE>30>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>30>VOLUME>1^MUTE|FALSE|U|<CRLF> |

| INPUT_DANTE>31>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>31>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| --- | --- | --- |
| INPUT_DANTE>32>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_DANTE>32>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_OS>1>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_OS>1>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_OS>2>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_OS>2>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| INPUT_GENERATOR>1>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^INPUT_GENERATOR>1>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>1>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>1>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>2>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>2>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>3>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>3>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>4>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>4>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>5>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>5>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>6>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>6>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>7>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>7>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>8>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>8>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>9>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>9>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>10>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>10>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>11>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>11>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>12>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>12>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>13>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>13>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>14>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>14>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>15>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>15>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>16>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>16>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>17>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>17>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>18>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>18>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>19>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>19>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>20>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>20>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>21>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>21>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>22>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>22>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>23>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>23>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>24>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>24>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>25>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>25>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>26>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>26>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>27>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>27>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>28>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>28>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>29>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>29>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>30>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>30>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>31>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>31>VOLUME>1^MUTE|FALSE|U|<CRLF> |
| ZONE>32>VOLUME>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^ZONE>32>VOLUME>1^MUTE|FALSE|U|<CRLF> |

#### Grouped
            Commands

### ALL_ZONES

example
            (default value): #|LUNA_U>1||SET_REQ^ALL_ZONES^MUTE|FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALS
                E^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | ZONE>1>VOLUME>1 |
| 2 | ZONE>2>VOLUME>1 |
| 3 | ZONE>3>VOLUME>1 |
| 4 | ZONE>4>VOLUME>1 |
| 5 | ZONE>5>VOLUME>1 |
| 6 | ZONE>6>VOLUME>1 |
| 7 | ZONE>7>VOLUME>1 |
| 8 | ZONE>8>VOLUME>1 |
| 9 | ZONE>9>VOLUME>1 |
| 10 | ZONE>10>VOLUME>1 |
| 11 | ZONE>11>VOLUME>1 |
| 12 | ZONE>12>VOLUME>1 |
| 13 | ZONE>13>VOLUME>1 |
| 14 | ZONE>14>VOLUME>1 |
| 15 | ZONE>15>VOLUME>1 |
| 16 | ZONE>16>VOLUME>1 |
| 17 | ZONE>17>VOLUME>1 |
| 18 | ZONE>18>VOLUME>1 |
| 19 | ZONE>19>VOLUME>1 |
| 20 | ZONE>20>VOLUME>1 |
| 21 | ZONE>21>VOLUME>1 |
| 22 | ZONE>22>VOLUME>1 |
| 23 | ZONE>23>VOLUME>1 |
| 24 | ZONE>24>VOLUME>1 |
| 25 | ZONE>25>VOLUME>1 |
| 26 | ZONE>26>VOLUME>1 |
| 27 | ZONE>27>VOLUME>1 |
| 28 | ZONE>28>VOLUME>1 |
| 29 | ZONE>29>VOLUME>1 |
| 30 | ZONE>30>VOLUME>1 |
| 31 | ZONE>31>VOLUME>1 |
| 32 | ZONE>32>VOLUME>1 |

### ALL_DANTE_IN

example
            (default value): #|LUNA_U>1||SET_REQ^ALL_DANTE_IN^MUTE|FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^F
                ALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | INPUT_DANTE>1>VOLUME>1 |
| 2 | INPUT_DANTE>2>VOLUME>1 |
| 3 | INPUT_DANTE>3>VOLUME>1 |
| 4 | INPUT_DANTE>4>VOLUME>1 |
| 5 | INPUT_DANTE>5>VOLUME>1 |
| 6 | INPUT_DANTE>6>VOLUME>1 |
| 7 | INPUT_DANTE>7>VOLUME>1 |
| 8 | INPUT_DANTE>8>VOLUME>1 |
| 9 | INPUT_DANTE>9>VOLUME>1 |
| 10 | INPUT_DANTE>10>VOLUME>1 |
| 11 | INPUT_DANTE>11>VOLUME>1 |
| 12 | INPUT_DANTE>12>VOLUME>1 |
| 13 | INPUT_DANTE>13>VOLUME>1 |
| 14 | INPUT_DANTE>14>VOLUME>1 |
| 15 | INPUT_DANTE>15>VOLUME>1 |
| 16 | INPUT_DANTE>16>VOLUME>1 |
| 17 | INPUT_DANTE>17>VOLUME>1 |
| 18 | INPUT_DANTE>18>VOLUME>1 |
| 19 | INPUT_DANTE>19>VOLUME>1 |
| 20 | INPUT_DANTE>20>VOLUME>1 |
| 21 | INPUT_DANTE>21>VOLUME>1 |
| 22 | INPUT_DANTE>22>VOLUME>1 |
| 23 | INPUT_DANTE>23>VOLUME>1 |
| 24 | INPUT_DANTE>24>VOLUME>1 |
| 25 | INPUT_DANTE>25>VOLUME>1 |
| 26 | INPUT_DANTE>26>VOLUME>1 |
| 27 | INPUT_DANTE>27>VOLUME>1 |
| 28 | INPUT_DANTE>28>VOLUME>1 |
| 29 | INPUT_DANTE>29>VOLUME>1 |
| 30 | INPUT_DANTE>30>VOLUME>1 |
| 31 | INPUT_DANTE>31>VOLUME>1 |
| 32 | INPUT_DANTE>32>VOLUME>1 |

### ALL_ANALOG_IN

example
            (default value):

#|LUNA_U>1||SET_REQ^ALL_ANALOG_IN^MUTE|FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | INPUT_LINE>1>VOLUME>1 |
| 2 | INPUT_LINE>2>VOLUME>1 |
| 3 | INPUT_LINE>3>VOLUME>1 |
| 4 | INPUT_LINE>4>VOLUME>1 |
| 5 | INPUT_LINE>5>VOLUME>1 |
| 6 | INPUT_LINE>6>VOLUME>1 |
| 7 | INPUT_LINE>7>VOLUME>1 |
| 8 | INPUT_LINE>8>VOLUME>1 |
| 9 | INPUT_LINE>9>VOLUME>1 |
| 10 | INPUT_LINE>10>VOLUME>1 |
| 11 | INPUT_LINE>11>VOLUME>1 |
| 12 | INPUT_LINE>12>VOLUME>1 |

### ALL_OS_IN

example
            (default value): #|LUNA_U>1||SET_REQ^ALL_OS_IN^MUTE|FALSE^FALSE^FALSE|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | INPUT_GENERATOR>1>VOLUME>1 |
| 2 | INPUT_OS>1>VOLUME>1 |
| 3 | INPUT_OS>2>VOLUME>1 |

### GPO_ENABLE

trigger
            a GPIO Output

### Argument
            (enable) : trigger the GP0

| Target | Argument | Example
                        (default value) |
| --- | --- | --- |
| GPO>1>GPO_TRIGGER>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^GPO>1>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>2>GPO_TRIGGER>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^GPO>2>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>3>GPO_TRIGGER>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^GPO>3>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>4>GPO_TRIGGER>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^GPO>4>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>5>GPO_TRIGGER>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^GPO>5>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>6>GPO_TRIGGER>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^GPO>6>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>7>GPO_TRIGGER>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^GPO>7>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>8>GPO_TRIGGER>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^GPO>8>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>9>GPO_TRIGGER>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^GPO>9>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>10>GPO_TRIGGER>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^GPO>10>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>11>GPO_TRIGGER>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^GPO>11>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>12>GPO_TRIGGER>1 | options:
                        TRUE,FALSE | #|LUNA_U>1||SET_REQ^GPO>12>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |

#### Grouped
            Commands

### ALL_GPIO

example
            (default value):

#|LUNA_U>1||SET_REQ^ALL_GPIO^GPO_ENABLE|FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | GPO>1>GPO_TRIGGER>1 |
| 2 | GPO>2>GPO_TRIGGER>1 |
| 3 | GPO>3>GPO_TRIGGER>1 |
| 4 | GPO>4>GPO_TRIGGER>1 |
| 5 | GPO>5>GPO_TRIGGER>1 |
| 6 | GPO>6>GPO_TRIGGER>1 |
| 7 | GPO>7>GPO_TRIGGER>1 |
| 8 | GPO>8>GPO_TRIGGER>1 |
| 9 | GPO>9>GPO_TRIGGER>1 |
| 10 | GPO>10>GPO_TRIGGER>1 |
| 11 | GPO>11>GPO_TRIGGER>1 |
| 12 | GPO>12>GPO_TRIGGER>1 |

### MIXER

mixer
            slider for zones

### Argument
            (volume) : mixing volume

| Target | Argument
                        Index | Argument | Example
                        (default value) |
| --- | --- | --- | --- |
| ZONE>1>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>1>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^10 <CRLF> |
| ZONE>2>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>2>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^10 <CRLF> |
| ZONE>3>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>3>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^10 <CRLF> |
| ZONE>4>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>4>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^10 <CRLF> |
| ZONE>5>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>5>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^10 <CRLF> |
| ZONE>6>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>6>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^10 <CRLF> |
| ZONE>7>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>7>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^10 <CRLF> |
| ZONE>8>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>8>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^10 <CRLF> |
| ZONE>9>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>9>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^10 <CRLF> |
| ZONE>10>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>10>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>11>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>11>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>12>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>12>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>13>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>13>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>14>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>14>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>15>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>15>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>16>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>16>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>17>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>17>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>18>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>18>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>19>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>19>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>20>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>20>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>21>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>21>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>22>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>22>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>23>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>23>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>24>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>24>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>25>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>25>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>26>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>26>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
|  |  |  |  |

| ZONE>27>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>27>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| --- | --- | --- | --- |
| ZONE>28>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>28>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>29>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>29>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>30>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>30>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>31>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>31>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |
| ZONE>32>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>32>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90^5>-90^6>-90^7>-90^8>-90^9>-90^1 <CRLF> |

### ROUTE

change
            the routing of a zone

### Argument
            (input) : the input that is selected in that zone. -1
                = Mixed (not settable), O = OFF, 1 = input 1
                ,...

| Target | Argument | Example
                        (default value) |
| --- | --- | --- |
| ZONE>1>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>1>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>2>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>2>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>3>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>3>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>4>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>4>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>5>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>5>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>6>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>6>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>7>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>7>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>8>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>8>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>9>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>9>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>10>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>10>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>11>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>11>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>12>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>12>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>13>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>13>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>14>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>14>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>15>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>15>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>16>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>16>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>17>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>17>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>18>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>18>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>19>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>19>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>20>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>20>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>21>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>21>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>22>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>22>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>23>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>23>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>24>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>24>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>25>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>25>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>26>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>26>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>27>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>27>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>28>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>28>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>29>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>29>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>30>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>30>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>31>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>31>MIXER>1^ROUTE|0|U|<CRLF> |
| ZONE>32>MIXER>1 | min:
                        -1, max: 24 | #|LUNA_U>1||SET_REQ^ZONE>32>MIXER>1^ROUTE|0|U|<CRLF> |

#### Grouped
            Commands

### ALL_ZONES

example
            (default value): #|LUNA_U>1||SET_REQ^ALL_ZONES^ROUTE|0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | ZONE>1>MIXER>1 |
| 2 | ZONE>2>MIXER>1 |
| 3 | ZONE>3>MIXER>1 |
| 4 | ZONE>4>MIXER>1 |
| 5 | ZONE>5>MIXER>1 |
| 6 | ZONE>6>MIXER>1 |
| 7 | ZONE>7>MIXER>1 |
| 8 | ZONE>8>MIXER>1 |
| 9 | ZONE>9>MIXER>1 |
| 10 | ZONE>10>MIXER>1 |
| 11 | ZONE>11>MIXER>1 |
| 12 | ZONE>12>MIXER>1 |
| 13 | ZONE>13>MIXER>1 |
| 14 | ZONE>14>MIXER>1 |
| 15 | ZONE>15>MIXER>1 |
| 16 | ZONE>16>MIXER>1 |
| 17 | ZONE>17>MIXER>1 |
| 18 | ZONE>18>MIXER>1 |
| 19 | ZONE>19>MIXER>1 |
| 20 | ZONE>20>MIXER>1 |
| 21 | ZONE>21>MIXER>1 |
| 22 | ZONE>22>MIXER>1 |
| 23 | ZONE>23>MIXER>1 |
| 24 | ZONE>24>MIXER>1 |
| 25 | ZONE>25>MIXER>1 |
| 26 | ZONE>26>MIXER>1 |
| 27 | ZONE>27>MIXER>1 |
| 28 | ZONE>28>MIXER>1 |
| 29 | ZONE>29>MIXER>1 |
| 30 | ZONE>30>MIXER>1 |
| 31 | ZONE>31>MIXER>1 |
| ‌ 32 | ZONE>32>MIXER>1 |

## CRC

The
            CRC block is calculated over the message starting from and including
            the first pipe "|", up to and including the last pipe before the CRC Block. These CRC's can ensure message
            integrity if desired.

| CRC
                        Type | Configuration | Format | Example | notes |
| --- | --- | --- | --- | --- |
| None | / | U | `#|ALL||SET_REQ^INPUT_LINE>1^VOLUME|0|U|<CRLF> ` | 'U'
                        means unused |
| CRC16-ARC | input
                        reflected output reflected polynomial: 0x8005 initial
                        value: 0x0000 final exor: 0x0000 | XXXX | `#|ALL||SET_REQ^INPUT_LINE>1^VOLUME|0|C06C|<CRLF> ` | calculator |
| CRC32 | input
                        reflected output reflected polynomial:
                        0x04C11DB7 initial value: 0xFFFFFFFF final exor:
                        0xFFFFFFFF | XXXXXXXX | `#|ALL||SET_REQ^INPUT_LINE>1^VOLUME|0|D887125C|<CRLF> ` | calculator |

The
            examples in the table above are example for calculating the CRC,
            they may not be a valid command for the Luna U

The
            CRC can ensure data integrity accross unreliable data channels
            (RS232, RS485), but they are by no means a security measure! If
            someone has the knowledge and means to maliciously alter a message,
            correcting the CRC becomes trivial for the attacker. We support
            different kinds of CRC for maximum flexibility, but we recommend not
            using any so you do not get a false sense of security.

## Stop
            Bytes

The
            final 2 characters are denoted as <CRLF>, they mean
            "Carriage Return, Line Feed" or simply put a new line.
            Depending on the tool used to create the command, you can have
            different representations:

CRLF

\r\n

0x0D
            0x0A

We
            support both CRLF and LF only

#### Luna-U
            Commands List - V1.6

# ASCII
            Commands (Luna U V1.6.0)

This is
            the list of ASCII Commands supported by this device. An ASCII
            command always follows the same structure:

#|Destination|Source|Type^Target^Command|Arguments|CRC|CRLF

This
            format uses 3 separator characters for different levels of
            separating each value in the message:

Message
            separator '|':

This
            separates a message in 7 blocks (if you include the start
            '#' and end <CRLF>)

Block
            separator '^':

This
            splits a block into logical elements. This is used to split the
            command in the message type, 'command' and
            'target'

Value
            separator '>':

This
            splits up a logical single value in their primitives, for example: a
            target consists of a channel type and a channel index, split by
            '>'

### Messages
            are Case sensitive, if the example shows the text in uppercase, this
            should always be uppercase!

## Destination

The
            target device. This consists of 2 parts: Device>Address .

### Device

This
            is the device type: LUNA_U

### Address

This
            is the user configurable device address, default: 1 . You can
            also leave this field empty, this results in all Luna U devices that
            receive this command to respond.

| Examples | Destination |
| --- | --- |
| default
                        destination | LUNA_U>1 |
| broadcast
                        to all Luna U devices | LUNA_U |

### Device
            Matching

| Destination | Matches | Remarks |
| --- | --- | --- |
| LUNA_U>2 | Destination
                        Matches Device | this
                        is an exact match |
| LUNA_U>1 | Message
                        ignored | the
                        destination address does not match |
| LUNA_U | Destination
                        Matches Device | the
                        destination address will always match |
| LUNA_U>0 | Destination
                        Matches Device | Equivalent
                        to LUNA_U |
| CLIENT>2 | Message
                        ignored | the
                        device type does not match |
| CLIENT | Message
                        ignored | the
                        device type does not match |

If
            the device type or address does not match, the message will be
            ignored. Device Address 0 is a special address and will always match
            (this can be seen as a broadcast) The table below describes if a
            message is accepted with a device that has address: LUNA_U>2

## Source
            (optional)

The
            source address is optional when sending, but the device will always
            fill this field with its own address. The table below the responses
            of a device with address: LUNA_U>2

| Examples | Message | Response |
| --- | --- | --- |
| broadcast
                        to a Luna U | #|LUNA_U||...|<CRLF> | #||LUNA_U>2|...|<CRLF> |
| send
                        to a specific Luna U | #|LUNA_U>2||...|<CRLF> | #||LUNA_U>2|...|<CRLF> |
| use
                        a source address in the request message | #|LUNA_U|CLIENT>1|...|<CRLF> | #|CLIENT>1|LUNA_U>2|...|<CRLF> |

## Type

The
            type explains what the message wants to do. There are 4 supported
            message types:

| Type | From | To | Explanation |
| --- | --- | --- | --- |
| SET_REQ | CLIENT | Luna
                        U | Change
                        a setting in the Luna U. If the value you send is
                        invalid (too high, too low, not a valid stepsize, ...)
                        the device does nothing |
| SET_FRC | CLIENT | Luna
                        U | Change
                        a setting in the Luna U. If the value you send is
                        invalid, the device will clamp to the closest allowed
                        value. This is especially useful if you don't know
                        the limits, or if you are using UP/DOWN
                        commands |
| GET_REQ | CLIENT | Luna
                        U | Request
                        the current status of a setting in the Luna
                        U |
| GET_RSP | Luna
                        U | CLIENT | Response
                        to either a GET_REQ or SET_REQ, if the request was
                        valid |

## Command,
            Target, Arguments

These
            3 parameters are explained together, because they influence each
            other. The command dictates the meaning of the argument, while the
            target distinguishes which exact setting you want to change. the
            target can also influence the valid range of the argument.

Some
            commands (like the mixer) can have a range arguments (for the mixer:
            all mixer volumes are an individual argument). In this case, the
            argument looks like:

idx>val[^idx2>val2] , where the part in between the brackets [] can appear 0 or more times.

idx,
            ídx2, ...: the argument index

val,
            val2, ...: the value at the specified index

### Grouped
            Commands

This
            device supports special ALL_* commands that
            allow you to set multiple values in a single command. They look
            similar to their single counterparts, but the Target

starts
            with ALL_ . The Argument is an array
            of elements, separated by "block separators", instead of a
            single value. For example: if there's a device that supports
            grouping 2 MUTE commands, the following can be shortened:

#|LUNA_U>1||SET_REQ^TARGET>1^MUTE|TRUE|U|<CRLF>
            #|LUNA_U>1||SET_REQ^TARGET>2^MUTE|TRUE|U|<CRLF>

becomes

#|LUNA_U>1||SET_REQ^ALL_TARGET^MUTE|TRUE^TRUE|U|<CRLF>

Note:
            For backwards compatibility reasons there might be gaps in the
            arguments sent, it is important to leave these gaps in the command
            you build! A gap is created by putting 2 block separators next to
            each other: "^^".

You
            can leverage this as well, if there are parts of this grouped
            command you don't want to change. You can then leave this value
            empty like the gaps, and you can only change the values you want,
            leaving the rest as is.

TRUE^^FALSE : Set the first value to true, leave the second value
                as is, set the third value to false.

You
            can also skip the last elements in the list, if you don't want
            to change them. For example: the command groups 4 volumes together,
            all. If you only want to change the first two values, you have 2
            options for the "Arguments" field:

-15^-30^^

-15^-30

Both
            are equivalent, but in the first example you explicitly define the
            third and fourth values as "gaps", in the second example
            they are implicitly defined as gaps.

### UP/DOWN
            Commands

Instead
            of always sending an absolute value of a command that contains a
            number, you can also send commands to increase, or decrease the
            value. You do this by instead of sending only a number as argument,
            you send U<amount> or D<amount> . <amount> is how much you want to
            increase or decrease the value with.

Some
            notes:

You
            have to specify a number, omitting the number will be seen as U0 or D0 . While this
            command is accepted and will generate a response, it won't
            change the value!

You
            can specify negative numbers, U-1 is the
            same D1 and vice-versa.

You
            can also use these UP/DOWN commands in the grouped
                commands . You can mix and match with absolute values
            within the same command.

It's
            important to note the distinction between SET_FRC and SET_REQ with
            relative commands. This is best explained using an example. If the
            current value of something is -8, and the maximum allowed value is
            0, and you want to increase the value by 10 ( U10 ) you can send this with SET_FRC or
            SET_REQ

SET_FRC
            will force the value within the limits, resulting in the value being
            set to 0

SET_REQ
            will validate the value to the limits, detect it would try to set
            +2, which is outside the limits, and do nothing.

## Command
            List

### APPLY_SNAPSHOT

applies
            a snapshot

### Argument
            (id) : the name of the snapshot to
                apply

| Target | Argument | Example(s) |
| --- | --- | --- |
| SNAPSHOTS>1 | regex: ^(settings\/snapshots\/)
                        [a-zA-Z0-9 _-]+\.snapshot$ | Default
                        value: #|LUNA_U>1||SET_REQ^SNAPSHOTS>1^APPLY_SNAPSHOT|settings/snapshots/New
                        Sna |

### GPO_ENABLE

trigger
            a GPIO Output

### Argument
            (enable) : trigger the GP0

| Target | Argument | Example(s) |
| --- | --- | --- |
| GPO>1>GPO_TRIGGER>1 | TRUE
                        FALSE TOGGLE | Default
                        value: #|LUNA_U>1||SET_REQ^GPO>1>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>2>GPO_TRIGGER>1 | TRUE
                        FALSE TOGGLE | Default
                        value: #|LUNA_U>1||SET_REQ^GPO>2>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>3>GPO_TRIGGER>1 | TRUE
                        FALSE TOGGLE | Default
                        value: #|LUNA_U>1||SET_REQ^GPO>3>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>4>GPO_TRIGGER>1 | TRUE
                        FALSE TOGGLE | Default
                        value: #|LUNA_U>1||SET_REQ^GPO>4>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>5>GPO_TRIGGER>1 | TRUE
                        FALSE TOGGLE | Default
                        value: #|LUNA_U>1||SET_REQ^GPO>5>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>6>GPO_TRIGGER>1 | TRUE
                        FALSE TOGGLE | Default
                        value: #|LUNA_U>1||SET_REQ^GPO>6>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>7>GPO_TRIGGER>1 | TRUE
                        FALSE TOGGLE | Default
                        value: #|LUNA_U>1||SET_REQ^GPO>7>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>8>GPO_TRIGGER>1 | TRUE
                        FALSE TOGGLE | Default
                        value: #|LUNA_U>1||SET_REQ^GPO>8>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>9>GPO_TRIGGER>1 | TRUE
                        FALSE TOGGLE | Default
                        value: #|LUNA_U>1||SET_REQ^GPO>9>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>10>GPO_TRIGGER>1 | TRUE
                        FALSE TOGGLE | Default
                        value: #|LUNA_U>1||SET_REQ^GPO>10>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>11>GPO_TRIGGER>1 | TRUE
                        FALSE TOGGLE | Default
                        value: #|LUNA_U>1||SET_REQ^GPO>11>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |
| GPO>12>GPO_TRIGGER>1 | TRUE
                        FALSE TOGGLE | Default
                        value: #|LUNA_U>1||SET_REQ^GPO>12>GPO_TRIGGER>1^GPO_ENABLE|FALSE|U|<CRLF> |

#### Grouped
            Commands

### ALL_GPIO

example
            (default value):

#|LUNA_U>1||SET_REQ^ALL_GPIO^GPO_ENABLE|FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | GPO>1>GPO_TRIGGER>1 |
| 2 | GPO>2>GPO_TRIGGER>1 |
| 3 | GPO>3>GPO_TRIGGER>1 |
| 4 | GPO>4>GPO_TRIGGER>1 |
| 5 | GPO>5>GPO_TRIGGER>1 |
| 6 | GPO>6>GPO_TRIGGER>1 |
| 7 | GPO>7>GPO_TRIGGER>1 |
| 8 | GPO>8>GPO_TRIGGER>1 |
| 9 | GPO>9>GPO_TRIGGER>1 |
| 10 | GPO>10>GPO_TRIGGER>1 |
| 11 | GPO>11>GPO_TRIGGER>1 |
| 12 | GPO>12>GPO_TRIGGER>1 |

### MIXER

mixer
            slider for zones

### Argument
            (volume) : mixing volume

| Target | Argument
                        Index | Argument | Example(s) |
| --- | --- | --- | --- |
| ZONE>1>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>1>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90
                        #|LUNA_U>1||SET_FRC^ZONE>1>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5>U |
| ZONE>2>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>2>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90
                        #|LUNA_U>1||SET_FRC^ZONE>2>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5>U |
| ZONE>3>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>3>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90
                        #|LUNA_U>1||SET_FRC^ZONE>3>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5>U |
| ZONE>4>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>4>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90
                        #|LUNA_U>1||SET_FRC^ZONE>4>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5>U |
| ZONE>5>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>5>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90
                        #|LUNA_U>1||SET_FRC^ZONE>5>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5>U |
| ZONE>6>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>6>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90
                        #|LUNA_U>1||SET_FRC^ZONE>6>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5>U |
| ZONE>7>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>7>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90
                        #|LUNA_U>1||SET_FRC^ZONE>7>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5>U |
| ZONE>8>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>8>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90
                        #|LUNA_U>1||SET_FRC^ZONE>8>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5>U |
| ZONE>9>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>9>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-90
                        #|LUNA_U>1||SET_FRC^ZONE>9>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5>U |
| ZONE>10>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>10>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>10>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>11>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>11>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>11>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>12>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>12>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA U>1||SET
                        FRC^ZONE>12>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5 |

|  |  | stepsize:
                        1 |  |
| --- | --- | --- | --- |
| ZONE>13>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>13>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>13>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>14>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>14>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>14>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>15>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>15>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>15>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>16>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>16>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>16>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>17>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>17>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>17>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>18>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>18>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>18>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>19>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>19>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>19>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>20>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>20>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>20>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>21>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>21>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>21>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>22>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>22>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>22>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>23>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>23>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>23>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>24>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 | #|LUNA_U>1||SET_REQ^ZONE>24>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>24>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |

|  |  | stepsize:
                        1 |  |
| --- | --- | --- | --- |
| ZONE>25>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>25>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>25>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>26>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>26>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>26>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>27>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>27>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>27>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>28>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>28>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>28>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>29>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>29>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>29>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>30>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>30>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>30>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>31>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>31>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>31>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |
| ZONE>32>MIXER>1 | min:
                        1, max:
                        16 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>32>MIXER>1^MIXER|1>-90^2>-90^3>-90^4>-9
                        #|LUNA_U>1||SET_FRC^ZONE>32>MIXER>1^MIXER|1>U1^2>D1^3>U1^4>D1^5> |

### MUTE

mute an
            audio channel

### Argument
            (enabled) : is the audio channel muted

Target

Argument

Example(s)

INPUT_LINE>1>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_LINE>1>VOLUME>1^MUTE|FALSE|U|<

INPUT_LINE>2>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_LINE>2>VOLUME>1^MUTE|FALSE|U|<

INPUT_LINE>3>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_LINE>3>VOLUME>1^MUTE|FALSE|U|<

INPUT_LINE>4>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_LINE>4>VOLUME>1^MUTE|FALSE|U|<

INPUT_LINE>5>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_LINE>5>VOLUME>1^MUTE|FALSE|U|<

INPUT_LINE>6>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_LINE>6>VOLUME>1^MUTE|FALSE|U|<

INPUT_LINE>7>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_LINE>7>VOLUME>1^MUTE|FALSE|U|<

INPUT_LINE>8>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_LINE>8>VOLUME>1^MUTE|FALSE|U|<

INPUT_LINE>9>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_LINE>9>VOLUME>1^MUTE|FALSE|U|<

INPUT_LINE>10>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_LINE>10>VOLUME>1^MUTE|FALSE|U|

INPUT_LINE>11>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_LINE>11>VOLUME>1^MUTE|FALSE|U|

INPUT_LINE>12>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_LINE>12>VOLUME>1^MUTE|FALSE|U|

INPUT_DANTE>1>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>1>VOLUME>1^MUTE|FALSE|U|

INPUT_DANTE>2>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>2>VOLUME>1^MUTE|FALSE|U|

INPUT_DANTE>3>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>3>VOLUME>1^MUTE|FALSE|U|

INPUT_DANTE>4>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>4>VOLUME>1^MUTE|FALSE|U|

INPUT
            DANTE>5>VOLUME>1

TRUE
            FALSE

Default
            value:

TOGGLE

#|LUNA_U>1||SET_REQ^INPUT_DANTE>5>VOLUME>1^MUTE|FALSE|U|

INPUT_DANTE>6>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>6>VOLUME>1^MUTE|FALSE|U|

INPUT_DANTE>7>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>7>VOLUME>1^MUTE|FALSE|U|

INPUT_DANTE>8>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>8>VOLUME>1^MUTE|FALSE|U|

INPUT_DANTE>9>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>9>VOLUME>1^MUTE|FALSE|U|

INPUT_DANTE>10>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>10>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>11>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>11>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>12>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>12>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>13>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>13>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>14>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>14>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>15>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>15>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>16>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>16>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>17>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>17>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>18>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>18>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>19>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>19>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>20>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>20>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>21>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>21>VOLUME>1^MUTE|FALSE|U

TRUE
            FALSE

Default
            value:

INPUT_DANTE>22>VOLUME>1

TOGGLE

#|LUNA_U>1||SET_REQ^INPUT_DANTE>22>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>23>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>23>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>24>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>24>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>25>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>25>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>26>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>26>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>27>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>27>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>28>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>28>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>29>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>29>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>30>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>30>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>31>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>31>VOLUME>1^MUTE|FALSE|U

INPUT_DANTE>32>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_DANTE>32>VOLUME>1^MUTE|FALSE|U

INPUT_OS>1>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_OS>1>VOLUME>1^MUTE|FALSE|U|<CR

INPUT_OS>2>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_OS>2>VOLUME>1^MUTE|FALSE|U|<CR

INPUT_GENERATOR>1>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^INPUT_GENERATOR>1>VOLUME>1^MUTE|FALS

ZONE>1>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>1>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>2>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>2>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>3>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>3>VOLUME>1^MUTE|FALSE|U|<CRLF>

TRUE
            Default value:

ZONE>4>VOLUME>1

FALSE
            TOGGLE

#|LUNA_U>1||SET_REQ^ZONE>4>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>5>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>5>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>6>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>6>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>7>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>7>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>8>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>8>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>9>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>9>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>10>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>10>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>11>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>11>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>12>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>12>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>13>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>13>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>14>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>14>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>15>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>15>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>16>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>16>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>17>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>17>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>18>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>18>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>19>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>19>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>20>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>20>VOLUME>1^MUTE|FALSE|U|<CRLF>

TRUE
            Default value:

ZONE>21>VOLUME>1

FALSE
            TOGGLE

#|LUNA_U>1||SET_REQ^ZONE>21>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>22>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>22>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>23>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>23>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>24>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>24>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>25>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>25>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>26>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>26>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>27>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>27>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>28>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>28>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>29>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>29>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>30>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>30>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>31>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>31>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONE>32>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONE>32>VOLUME>1^MUTE|FALSE|U|<CRLF>

ZONEMONO_AUTOMIXER>1>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONEMONO_AUTOMIXER>1>VOLUME>1^MUTE|F

ZONEMONO_AUTOMIXER>2>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONEMONO_AUTOMIXER>2>VOLUME>1^MUTE|F

ZONEMONO_AUTOMIXER>3>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONEMONO_AUTOMIXER>3>VOLUME>1^MUTE|F

ZONEMONO_AUTOMIXER>4>VOLUME>1

TRUE
            FALSE TOGGLE

Default
            value:

#|LUNA_U>1||SET_REQ^ZONEMONO_AUTOMIXER>4>VOLUME>1^MUTE|F

#### Grouped
            Commands

### ALL_ZONES

example
            (default value):

#|LUNA_U>1||SET_REQ^ALL_ZONES^MUTE|FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALS

| Index | Target |
| --- | --- |
| 1 | ZONE>1>VOLUME>1 |
| 2 | ZONE>2>VOLUME>1 |
| 3 | ZONE>3>VOLUME>1 |
| 4 | ZONE>4>VOLUME>1 |
| 5 | ZONE>5>VOLUME>1 |
| 6 | ZONE>6>VOLUME>1 |
| 7 | ZONE>7>VOLUME>1 |
| 8 | ZONE>8>VOLUME>1 |
| 9 | ZONE>9>VOLUME>1 |
| 10 | ZONE>10>VOLUME>1 |
| 11 | ZONE>11>VOLUME>1 |
| 12 | ZONE>12>VOLUME>1 |
| 13 | ZONE>13>VOLUME>1 |
| 14 | ZONE>14>VOLUME>1 |
| 15 | ZONE>15>VOLUME>1 |
| 16 | ZONE>16>VOLUME>1 |
| 17 | ZONE>17>VOLUME>1 |
| 18 | ZONE>18>VOLUME>1 |
| 19 | ZONE>19>VOLUME>1 |
| 20 | ZONE>20>VOLUME>1 |
| 21 | ZONE>21>VOLUME>1 |
| 22 | ZONE>22>VOLUME>1 |
| 23 | ZONE>23>VOLUME>1 |
| 24 | ZONE>24>VOLUME>1 |
| 25 | ZONE>25>VOLUME>1 |
| 26 | ZONE>26>VOLUME>1 |
| 27 | ZONE>27>VOLUME>1 |
| 28 | ZONE>28>VOLUME>1 |
| 29 | ZONE>29>VOLUME>1 |
| 30 | ZONE>30>VOLUME>1 |
| 31 | ZONE>31>VOLUME>1 |
| 32 | ZONE>32>VOLUME>1 |

### ALL_DANTE_IN

example
            (default value):

#|LUNA_U>1||SET_REQ^ALL_DANTE_IN^MUTE|FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^F

| Index | Target |
| --- | --- |
| 1 | INPUT_DANTE>1>VOLUME>1 |
| 2 | INPUT_DANTE>2>VOLUME>1 |
| 3 | INPUT_DANTE>3>VOLUME>1 |
| 4 | INPUT_DANTE>4>VOLUME>1 |
| 5 | INPUT_DANTE>5>VOLUME>1 |
| 6 | INPUT_DANTE>6>VOLUME>1 |
| 7 | INPUT_DANTE>7>VOLUME>1 |
| 8 | INPUT_DANTE>8>VOLUME>1 |
| 9 | INPUT_DANTE>9>VOLUME>1 |
| 10 | INPUT_DANTE>10>VOLUME>1 |
| 11 | INPUT_DANTE>11>VOLUME>1 |
| 12 | INPUT_DANTE>12>VOLUME>1 |
| 13 | INPUT_DANTE>13>VOLUME>1 |
| 14 | INPUT_DANTE>14>VOLUME>1 |
| 15 | INPUT_DANTE>15>VOLUME>1 |
| 16 | INPUT_DANTE>16>VOLUME>1 |
| 17 | INPUT_DANTE>17>VOLUME>1 |
| 18 | INPUT_DANTE>18>VOLUME>1 |
| 19 | INPUT_DANTE>19>VOLUME>1 |
| 20 | INPUT_DANTE>20>VOLUME>1 |
| 21 | INPUT_DANTE>21>VOLUME>1 |
| 22 | INPUT_DANTE>22>VOLUME>1 |
| 23 | INPUT_DANTE>23>VOLUME>1 |
| 24 | INPUT_DANTE>24>VOLUME>1 |
| 25 | INPUT_DANTE>25>VOLUME>1 |
| 26 | INPUT_DANTE>26>VOLUME>1 |
| 27 | INPUT_DANTE>27>VOLUME>1 |
| 28 | INPUT_DANTE>28>VOLUME>1 |
| 29 | INPUT_DANTE>29>VOLUME>1 |
| 30 | INPUT_DANTE>30>VOLUME>1 |
| 31 | INPUT_DANTE>31>VOLUME>1 |
| 32 | INPUT_DANTE>32>VOLUME>1 |

### ALL_ANALOG_IN

example
            (default value):

#|LUNA_U>1||SET_REQ^ALL_ANALOG_IN^MUTE|FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE^FALSE|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | INPUT_LINE>1>VOLUME>1 |
| 2 | INPUT_LINE>2>VOLUME>1 |
| 3 | INPUT_LINE>3>VOLUME>1 |
| 4 | INPUT_LINE>4>VOLUME>1 |
| 5 | INPUT_LINE>5>VOLUME>1 |
| 6 | INPUT_LINE>6>VOLUME>1 |
| 7 | INPUT_LINE>7>VOLUME>1 |
| 8 | INPUT_LINE>8>VOLUME>1 |
| 9 | INPUT_LINE>9>VOLUME>1 |
| 10 | INPUT_LINE>10>VOLUME>1 |
| 11 | INPUT_LINE>11>VOLUME>1 |
| 12 | INPUT_LINE>12>VOLUME>1 |

### ALL_OS_IN

example
            (default value):

#|LUNA_U>1||SET_REQ^ALL_OS_IN^MUTE|FALSE^FALSE^FALSE|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | INPUT_GENERATOR>1>VOLUME>1 |
| 2 | INPUT_OS>1>VOLUME>1 |
| 3 | INPUT_OS>2>VOLUME>1 |

### ALL_AUTOMIXERS

example
            (default value):

#|LUNA_U>1||SET_REQ^ALL_AUTOMIXERS^MUTE|FALSE^FALSE^FALSE^FALSE|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | ZONEMONO_AUTOMIXER>1>VOLUME>1 |
| 2 | ZONEMONO_AUTOMIXER>2>VOLUME>1 |
| 3 | ZONEMONO_AUTOMIXER>3>VOLUME>1 |
| 4 | ZONEMONO_AUTOMIXER>4>VOLUME>1 |

### ROUTE

change
            the routing of a zone

### Argument
            (input) : the input that is selected in that zone. -1
                = Mixed (not settable), O = OFF, 1 = input 1
                ,...

| Target | Argument | Example(s) |
| --- | --- | --- |
| ZONE>1>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>1>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>1>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>2>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>2>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>2>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>3>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>3>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>3>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>4>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>4>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>4>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>5>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>5>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>5>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>6>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>6>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>6>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>7>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>7>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>7>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>8>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>8>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>8>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>9>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>9>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>9>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>10>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>10>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>10>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>11>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>11>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>11>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>12>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>12>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>12>MIXER>1^ROUTE|U1|U|<CRLF> |

|  |  |  |
| --- | --- | --- |
| ZONE>13>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>13>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>13>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>14>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>14>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>14>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>15>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>15>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>15>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>16>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>16>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>16>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>17>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>17>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>17>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>18>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>18>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>18>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>19>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>19>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>19>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>20>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>20>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>20>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>21>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>21>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>21>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>22>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>22>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>22>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>23>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>23>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>23>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>24>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>24>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>24>MIXER>1^ROUTE|U1|U|<CRLF> |

|  |  |  |
| --- | --- | --- |
| ZONE>25>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>25>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>25>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>26>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>26>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>26>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>27>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>27>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>27>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>28>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>28>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>28>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>29>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>29>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>29>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>30>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>30>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>30>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>31>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>31>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>31>MIXER>1^ROUTE|U1|U|<CRLF> |
| ZONE>32>MIXER>1 | min:
                        -1, max:
                        24 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>32>MIXER>1^ROUTE|0|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>32>MIXER>1^ROUTE|U1|U|<CRLF> |

#### Grouped
            Commands

### ALL_ZONES

example
            (default value):

#|LUNA_U>1||SET_REQ^ALL_ZONES^ROUTE|0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | ZONE>1>MIXER>1 |
| 2 | ZONE>2>MIXER>1 |
| 3 | ZONE>3>MIXER>1 |
| 4 | ZONE>4>MIXER>1 |
| 5 | ZONE>5>MIXER>1 |
| 6 | ZONE>6>MIXER>1 |
| 7 | ZONE>7>MIXER>1 |
| 8 | ZONE>8>MIXER>1 |
| 9 | ZONE>9>MIXER>1 |
| 10 | ZONE>10>MIXER>1 |
| 11 | ZONE>11>MIXER>1 |
| 12 | ZONE>12>MIXER>1 |
| 13 | ZONE>13>MIXER>1 |
| 14 | ZONE>14>MIXER>1 |
| 15 | ZONE>15>MIXER>1 |
| 16 | ZONE>16>MIXER>1 |
| 17 | ZONE>17>MIXER>1 |
| 18 | ZONE>18>MIXER>1 |
| 19 | ZONE>19>MIXER>1 |
| 20 | ZONE>20>MIXER>1 |
| 21 | ZONE>21>MIXER>1 |
| 22 | ZONE>22>MIXER>1 |
| 23 | ZONE>23>MIXER>1 |
| 24 | ZONE>24>MIXER>1 |
| 25 | ZONE>25>MIXER>1 |
| 26 | ZONE>26>MIXER>1 |
| 27 | ZONE>27>MIXER>1 |
| 28 | ZONE>28>MIXER>1 |
| 29 | ZONE>29>MIXER>1 |
| 30 | ZONE>30>MIXER>1 |
| 31 | ZONE>31>MIXER>1 |
| 32 | ZONE>32>MIXER>1 |

### VOLUME

Set a
            single Volume in dB

### Argument
            (volume) : the requested Volume in
                dB

| Target | Argument | Example(s) |
| --- | --- | --- |
| INPUT_LINE>1>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_LINE>1>VOLUME>1^VOLUME|0|U|<C
                        #|LUNA_U>1||SET_FRC^INPUT_LINE>1>VOLUME>1^VOLUME|U1|U|< |
| INPUT_LINE>2>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_LINE>2>VOLUME>1^VOLUME|0|U|<C
                        #|LUNA_U>1||SET_FRC^INPUT_LINE>2>VOLUME>1^VOLUME|U1|U|< |
| INPUT_LINE>3>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_LINE>3>VOLUME>1^VOLUME|0|U|<C
                        #|LUNA_U>1||SET_FRC^INPUT_LINE>3>VOLUME>1^VOLUME|U1|U|< |
| INPUT_LINE>4>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_LINE>4>VOLUME>1^VOLUME|0|U|<C
                        #|LUNA_U>1||SET_FRC^INPUT_LINE>4>VOLUME>1^VOLUME|U1|U|< |
| INPUT_LINE>5>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_LINE>5>VOLUME>1^VOLUME|0|U|<C
                        #|LUNA_U>1||SET_FRC^INPUT_LINE>5>VOLUME>1^VOLUME|U1|U|< |
| INPUT_LINE>6>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_LINE>6>VOLUME>1^VOLUME|0|U|<C
                        #|LUNA_U>1||SET_FRC^INPUT_LINE>6>VOLUME>1^VOLUME|U1|U|< |
| INPUT_LINE>7>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_LINE>7>VOLUME>1^VOLUME|0|U|<C
                        #|LUNA_U>1||SET_FRC^INPUT_LINE>7>VOLUME>1^VOLUME|U1|U|< |
| INPUT_LINE>8>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_LINE>8>VOLUME>1^VOLUME|0|U|<C
                        #|LUNA_U>1||SET_FRC^INPUT_LINE>8>VOLUME>1^VOLUME|U1|U|< |
| INPUT_LINE>9>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_LINE>9>VOLUME>1^VOLUME|0|U|<C
                        #|LUNA_U>1||SET_FRC^INPUT_LINE>9>VOLUME>1^VOLUME|U1|U|< |
| INPUT_LINE>10>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_LINE>10>VOLUME>1^VOLUME|0|U|<
                        #|LUNA_U>1||SET_FRC^INPUT_LINE>10>VOLUME>1^VOLUME|U1|U| |
| INPUT_LINE>11>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_LINE>11>VOLUME>1^VOLUME|0|U|<
                        #|LUNA_U>1||SET_FRC^INPUT_LINE>11>VOLUME>1^VOLUME|U1|U| |
| INPUT_LINE>12>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_LINE>12>VOLUME>1^VOLUME|0|U|<
                        #|LUNA_U>1||SET_FRC^INPUT_LINE>12>VOLUME>1^VOLUME|U1|U| |

|  |  |  |
| --- | --- | --- |
| INPUT_DANTE>1>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>1>VOLUME>1^VOLUME|0|U|<
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>1>VOLUME>1^VOLUME|U1|U| |
| INPUT_DANTE>2>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>2>VOLUME>1^VOLUME|0|U|<
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>2>VOLUME>1^VOLUME|U1|U| |
| INPUT_DANTE>3>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>3>VOLUME>1^VOLUME|0|U|<
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>3>VOLUME>1^VOLUME|U1|U| |
| INPUT_DANTE>4>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>4>VOLUME>1^VOLUME|0|U|<
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>4>VOLUME>1^VOLUME|U1|U| |
| INPUT_DANTE>5>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>5>VOLUME>1^VOLUME|0|U|<
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>5>VOLUME>1^VOLUME|U1|U| |
| INPUT_DANTE>6>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>6>VOLUME>1^VOLUME|0|U|<
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>6>VOLUME>1^VOLUME|U1|U| |
| INPUT_DANTE>7>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>7>VOLUME>1^VOLUME|0|U|<
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>7>VOLUME>1^VOLUME|U1|U| |
| INPUT_DANTE>8>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>8>VOLUME>1^VOLUME|0|U|<
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>8>VOLUME>1^VOLUME|U1|U| |
| INPUT_DANTE>9>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>9>VOLUME>1^VOLUME|0|U|<
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>9>VOLUME>1^VOLUME|U1|U| |
| INPUT_DANTE>10>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>10>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>10>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>11>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>11>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>11>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>12>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>12>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>12>VOLUME>1^VOLUME|U1|U |

|  |  |  |
| --- | --- | --- |
| INPUT_DANTE>13>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>13>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>13>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>14>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>14>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>14>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>15>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>15>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>15>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>16>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>16>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>16>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>17>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>17>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>17>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>18>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>18>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>18>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>19>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>19>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>19>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>20>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>20>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>20>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>21>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>21>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>21>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>22>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>22>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>22>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>23>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>23>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>23>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>24>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>24>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>24>VOLUME>1^VOLUME|U1|U |

|  |  |  |
| --- | --- | --- |
| INPUT_DANTE>25>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>25>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>25>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>26>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>26>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>26>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>27>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>27>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>27>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>28>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>28>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>28>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>29>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>29>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>29>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>30>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>30>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>30>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>31>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>31>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>31>VOLUME>1^VOLUME|U1|U |
| INPUT_DANTE>32>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_DANTE>32>VOLUME>1^VOLUME|0|U|
                        #|LUNA_U>1||SET_FRC^INPUT_DANTE>32>VOLUME>1^VOLUME|U1|U |
| INPUT_OS>1>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_OS>1>VOLUME>1^VOLUME|0|U|<CRL
                        #|LUNA_U>1||SET_FRC^INPUT_OS>1>VOLUME>1^VOLUME|U1|U|<CR |
| INPUT_OS>2>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_OS>2>VOLUME>1^VOLUME|0|U|<CRL
                        #|LUNA_U>1||SET_FRC^INPUT_OS>2>VOLUME>1^VOLUME|U1|U|<CR |
| INPUT_GENERATOR>1>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^INPUT_GENERATOR>1>VOLUME>1^VOLUME|0
                        #|LUNA_U>1||SET_FRC^INPUT_GENERATOR>1>VOLUME>1^VOLUME|U |
| ZONE>1>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>1>VOLUME>1^VOLUME|-90|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>1>VOLUME>1^VOLUME|U1|U|<CRLF> |

|  |  |  |
| --- | --- | --- |
| ZONE>2>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>2>VOLUME>1^VOLUME|-90|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>2>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>3>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>3>VOLUME>1^VOLUME|-90|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>3>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>4>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>4>VOLUME>1^VOLUME|-90|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>4>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>5>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>5>VOLUME>1^VOLUME|-90|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>5>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>6>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>6>VOLUME>1^VOLUME|-90|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>6>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>7>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>7>VOLUME>1^VOLUME|-90|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>7>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>8>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>8>VOLUME>1^VOLUME|-90|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>8>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>9>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>9>VOLUME>1^VOLUME|-90|U|<CRLF>
                        #|LUNA_U>1||SET_FRC^ZONE>9>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>10>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>10>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>10>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>11>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>11>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>11>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>12>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>12>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>12>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>13>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>13>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>13>VOLUME>1^VOLUME|U1|U|<CRLF> |

| ZONE>14>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>14>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>14>VOLUME>1^VOLUME|U1|U|<CRLF> |
| --- | --- | --- |
| ZONE>15>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>15>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>15>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>16>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>16>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>16>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>17>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>17>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>17>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>18>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>18>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>18>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>19>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>19>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>19>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>20>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>20>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>20>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>21>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>21>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>21>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>22>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>22>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>22>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>23>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>23>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>23>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>24>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>24>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>24>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>25>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>25>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>25>VOLUME>1^VOLUME|U1|U|<CRLF> |

| ZONE>26>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>26>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>26>VOLUME>1^VOLUME|U1|U|<CRLF> |
| --- | --- | --- |
| ZONE>27>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>27>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>27>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>28>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>28>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>28>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>29>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>29>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>29>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>30>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>30>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>30>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>31>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>31>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>31>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONE>32>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONE>32>VOLUME>1^VOLUME|-90|U|<CRLF
                        #|LUNA_U>1||SET_FRC^ZONE>32>VOLUME>1^VOLUME|U1|U|<CRLF> |
| ZONEMONO_AUTOMIXER>1>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONEMONO_AUTOMIXER>1>VOLUME>1^VOLUM
                        #|LUNA_U>1||SET_FRC^ZONEMONO_AUTOMIXER>1>VOLUME>1^VOLUM |
| ZONEMONO_AUTOMIXER>2>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONEMONO_AUTOMIXER>2>VOLUME>1^VOLUM
                        #|LUNA_U>1||SET_FRC^ZONEMONO_AUTOMIXER>2>VOLUME>1^VOLUM |
| ZONEMONO_AUTOMIXER>3>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONEMONO_AUTOMIXER>3>VOLUME>1^VOLUM
                        #|LUNA_U>1||SET_FRC^ZONEMONO_AUTOMIXER>3>VOLUME>1^VOLUM |
| ZONEMONO_AUTOMIXER>4>VOLUME>1 | min:
                        -90, max:
                        0 stepsize:
                        1 | #|LUNA_U>1||SET_REQ^ZONEMONO_AUTOMIXER>4>VOLUME>1^VOLUM
                        #|LUNA_U>1||SET_FRC^ZONEMONO_AUTOMIXER>4>VOLUME>1^VOLUM |

#### Grouped
            Commands

### ALL_ZONES

example
            (default value):

#|LUNA_U>1||SET_REQ^ALL_ZONES^VOLUME|-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^-90^

| Index | Target |
| --- | --- |
| 1 | ZONE>1>VOLUME>1 |
| 2 | ZONE>2>VOLUME>1 |
| 3 | ZONE>3>VOLUME>1 |
| 4 | ZONE>4>VOLUME>1 |
| 5 | ZONE>5>VOLUME>1 |
| 6 | ZONE>6>VOLUME>1 |
| 7 | ZONE>7>VOLUME>1 |
| 8 | ZONE>8>VOLUME>1 |
| 9 | ZONE>9>VOLUME>1 |
| 10 | ZONE>10>VOLUME>1 |
| 11 | ZONE>11>VOLUME>1 |
| 12 | ZONE>12>VOLUME>1 |
| 13 | ZONE>13>VOLUME>1 |
| 14 | ZONE>14>VOLUME>1 |
| 15 | ZONE>15>VOLUME>1 |
| 16 | ZONE>16>VOLUME>1 |
| 17 | ZONE>17>VOLUME>1 |
| 18 | ZONE>18>VOLUME>1 |
| 19 | ZONE>19>VOLUME>1 |
| 20 | ZONE>20>VOLUME>1 |
| 21 | ZONE>21>VOLUME>1 |
| 22 | ZONE>22>VOLUME>1 |
| 23 | ZONE>23>VOLUME>1 |
| 24 | ZONE>24>VOLUME>1 |
| 25 | ZONE>25>VOLUME>1 |
| 26 | ZONE>26>VOLUME>1 |
| 27 | ZONE>27>VOLUME>1 |
| 28 | ZONE>28>VOLUME>1 |
| 29 | ZONE>29>VOLUME>1 |
| 30 | ZONE>30>VOLUME>1 |
| 31 | ZONE>31>VOLUME>1 |
| 32 | ZONE>32>VOLUME>1 |

### ALL_DANTE_IN

example
            (default value):

#|LUNA_U>1||SET_REQ^ALL_DANTE_IN^VOLUME|0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | INPUT_DANTE>1>VOLUME>1 |
| 2 | INPUT_DANTE>2>VOLUME>1 |
| 3 | INPUT_DANTE>3>VOLUME>1 |
| 4 | INPUT_DANTE>4>VOLUME>1 |
| 5 | INPUT_DANTE>5>VOLUME>1 |
| 6 | INPUT_DANTE>6>VOLUME>1 |
| 7 | INPUT_DANTE>7>VOLUME>1 |
| 8 | INPUT_DANTE>8>VOLUME>1 |
| 9 | INPUT_DANTE>9>VOLUME>1 |
| 10 | INPUT_DANTE>10>VOLUME>1 |
| 11 | INPUT_DANTE>11>VOLUME>1 |
| 12 | INPUT_DANTE>12>VOLUME>1 |
| 13 | INPUT_DANTE>13>VOLUME>1 |
| 14 | INPUT_DANTE>14>VOLUME>1 |
| 15 | INPUT_DANTE>15>VOLUME>1 |
| 16 | INPUT_DANTE>16>VOLUME>1 |
| 17 | INPUT_DANTE>17>VOLUME>1 |
| 18 | INPUT_DANTE>18>VOLUME>1 |
| 19 | INPUT_DANTE>19>VOLUME>1 |
| 20 | INPUT_DANTE>20>VOLUME>1 |
| 21 | INPUT_DANTE>21>VOLUME>1 |
| 22 | INPUT_DANTE>22>VOLUME>1 |
| 23 | INPUT_DANTE>23>VOLUME>1 |
| 24 | INPUT_DANTE>24>VOLUME>1 |
| 25 | INPUT_DANTE>25>VOLUME>1 |
| 26 | INPUT_DANTE>26>VOLUME>1 |
| 27 | INPUT_DANTE>27>VOLUME>1 |
| 28 | INPUT_DANTE>28>VOLUME>1 |
| 29 | INPUT_DANTE>29>VOLUME>1 |
| 30 | INPUT_DANTE>30>VOLUME>1 |
| 31 | INPUT_DANTE>31>VOLUME>1 |
| 32 | INPUT_DANTE>32>VOLUME>1 |

### ALL_ANALOG_IN

example
            (default value):

#|LUNA_U>1||SET_REQ^ALL_ANALOG_IN^VOLUME|0^0^0^0^0^0^0^0^0^0^0^0|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | INPUT_LINE>1>VOLUME>1 |
| 2 | INPUT_LINE>2>VOLUME>1 |
| 3 | INPUT_LINE>3>VOLUME>1 |
| 4 | INPUT_LINE>4>VOLUME>1 |
| 5 | INPUT_LINE>5>VOLUME>1 |
| 6 | INPUT_LINE>6>VOLUME>1 |
| 7 | INPUT_LINE>7>VOLUME>1 |
| 8 | INPUT_LINE>8>VOLUME>1 |
| 9 | INPUT_LINE>9>VOLUME>1 |
| 10 | INPUT_LINE>10>VOLUME>1 |
| 11 | INPUT_LINE>11>VOLUME>1 |
| 12 | INPUT_LINE>12>VOLUME>1 |

### ALL_OS_IN

example
            (default value):

#|LUNA_U>1||SET_REQ^ALL_OS_IN^VOLUME|0^0^0|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | INPUT_GENERATOR>1>VOLUME>1 |
| 2 | INPUT_OS>1>VOLUME>1 |
| 3 | INPUT_OS>2>VOLUME>1 |

### ALL_AUTOMIXERS

example
            (default value):

#|LUNA_U>1||SET_REQ^ALL_AUTOMIXERS^VOLUME|0^0^0^0|U|<CRLF>

| Index | Target |
| --- | --- |
| 1 | ZONEMONO_AUTOMIXER>1>VOLUME>1 |
| 2 | ZONEMONO_AUTOMIXER>2>VOLUME>1 |
| 3 | ZONEMONO_AUTOMIXER>3>VOLUME>1 |
| 4 | ZONEMONO_AUTOMIXER>4>VOLUME>1 |

## CRC

The
            CRC block is calculated over the message starting from and including
            the first pipe "|", up to and including the last pipe before the CRC Block. These CRC's can ensure message
            integrity if desired.

| CRC Type | Configuration | Format | Example | notes |
| --- | --- | --- | --- | --- |
| None | / | U | #|ALL||SET_REQ^INPUT_LINE>1^VOLUME|0|U|<CRLF> | 'U'
                        means unused |
| CRC16-ARC | input
                        reflected output reflected polynomial: 0x8005 initial
                        value: 0x0000 final
                        exor: 0x0000 | XXXX | #|ALL||SET_REQ^INPUT_LINE>1^VOLUME|0|C06C|<CRLF> | calculator |
| CRC32 | input
                        reflected output reflected polynomial: 0x04C11DB7 initial
                        value: 0xFFFFFFFF final
                        exor: 0xFFFFFFFF | XXXXXXXX | #|ALL||SET_REQ^INPUT_LINE>1^VOLUME|0|D887125C|<CRLF> | calculator |

The
            examples in the table above are examples for calculating the CRC,
            they may not be a valid command for the Luna U

The
            CRC can ensure data integrity accross unreliable data channels
            (RS232, RS485), but they are by no means a security measure! If
            someone has the knowledge and means to maliciously alter a message,
            correcting the CRC becomes trivial for the attacker. We support
            different kinds of CRC for maximum flexibility, but we recommend not
            using any so you do not get a false sense of security.

## Stop
            Bytes

The
            final 2 characters are denoted as <CRLF>, they mean
            "Carriage Return, Line Feed" or simply put a new line.
            Depending on the tool used to create the command, you can have
            different representations:

CRLF

\r\n

0x0D
            0x0A

We
            support both CRLF and LF only