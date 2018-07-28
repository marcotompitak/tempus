import sys
from os.path import dirname as d
from os.path import abspath, join
root_dir = d(d(abspath(__file__)))
sys.path.append(root_dir)

from utils.validation import validate_clockchain

def test_validate_clockchain():
    example_clockchain =\
        [
            {
                "55f5b323471532d860b11d4fc079ba38819567aa0915d83d4636d12e498a8f3e": {
                    "height": 0,
                    "list": [
                        {
                            "pubkey": "pubkey",
                            "timestamp": 0
                        }
                    ],
                    "nonce": 68696043434,
                    "prev_tick": "prev_tick",
                    "pubkey": "pubkey"
                }
            },
            {
                "38682de32a13ab059f249f1a04f38e7aad6a4d8ec60e9b26351384b2a11b0000": {
                    "height": 1,
                    "list": [
                        {
                            "nonce": 29202776895,
                            "pubkey": "cb02b479510318b28702e223f4365d540a39cca884a0a1e79aea92fcb4fc18c86d3b98ff0ff98cce2ed822067e84125dd0a83b928b5d52d64c321e4071cd08a9",
                            "reference": "55f5b323471532d860b11d4fc079ba38819567aa0915d83d4636d12e498a8f3e",
                            "signature": "9416e5e7eaca708f2142dda4dd2e3f59e9a552a0ce8b11d0355f4898b6b1c9cb3a0dab96284ae3f0de14d040326c7bf9d7b1b345559034b406434d64aa65f80b",
                            "timestamp": 1531165178
                        },
                        {
                            "nonce": 62932296770,
                            "pubkey": "79d95d151c5cd9487246d74e0788ebca8aea675b4f2235fb1a68234db43f04004d1b38e8f9fc41c3f88fb8d4e9b1f4909e34b2cb4b599ed72b0ceca3edac198e",
                            "reference": "55f5b323471532d860b11d4fc079ba38819567aa0915d83d4636d12e498a8f3e",
                            "signature": "deee487a8b5deca25cabe4bd87466b537b85262020dbf5b45ff082b9da3ee2bcb89d1a2e84ee5ba4be002968c73dd672a3d2261f4aecb611eb4066c2b14cdea1",
                            "timestamp": 1531165182
                        },
                        {
                            "nonce": 80176285626,
                            "pubkey": "f7bec1a681a8f9d00f93d6e84202ff3bc74f2b8e443d3118f32151b82976b7a0be568cc8fa7b8a8ed1963ce14861d63f3d6d06c905b9980223432b921b096ee8",
                            "reference": "55f5b323471532d860b11d4fc079ba38819567aa0915d83d4636d12e498a8f3e",
                            "signature": "9719e8fb4cd37b9068fad9b61f79324e9b39e009dab0a80aac7ef5b3344350e5e694b53044678c5ff10230352a278d1ca5daf3af7934a0d81e74c544874435d6",
                            "timestamp": 1531165177
                        }
                    ],
                    "nonce": 82343716680,
                    "prev_tick": "55f5b323471532d860b11d4fc079ba38819567aa0915d83d4636d12e498a8f3e",
                    "pubkey": "79d95d151c5cd9487246d74e0788ebca8aea675b4f2235fb1a68234db43f04004d1b38e8f9fc41c3f88fb8d4e9b1f4909e34b2cb4b599ed72b0ceca3edac198e",
                    "signature": "7c430b00870f0689e37456087e9b5bd19da4425cc7dcbab4a11faa443cd94ff77c4f83784d4c8087b666b784af0f9b1848e54b0e26347e156f91c55d6ccb541a"
                }
            },
            {
                "e00583e959b5f7f8080099281b94038e80a86f386a1b5bbe2e15bafa31d40000": {
                    "height": 2,
                    "list": [
                        {
                            "nonce": 45615523951,
                            "pubkey": "cb02b479510318b28702e223f4365d540a39cca884a0a1e79aea92fcb4fc18c86d3b98ff0ff98cce2ed822067e84125dd0a83b928b5d52d64c321e4071cd08a9",
                            "reference": "38682de32a13ab059f249f1a04f38e7aad6a4d8ec60e9b26351384b2a11b0000",
                            "signature": "94f34262cd72b21a369cf38622b9721bd6736492b0930933c4a5685ec3d7469d592ef3593a088be7d7bd2b6c27330ac8ac225a45dcb1a8f863c2057e17e0c1a7",
                            "timestamp": 1531165241
                        },
                        {
                            "nonce": 53542748053,
                            "pubkey": "79d95d151c5cd9487246d74e0788ebca8aea675b4f2235fb1a68234db43f04004d1b38e8f9fc41c3f88fb8d4e9b1f4909e34b2cb4b599ed72b0ceca3edac198e",
                            "reference": "38682de32a13ab059f249f1a04f38e7aad6a4d8ec60e9b26351384b2a11b0000",
                            "signature": "ff2cdfc9cabde54666f8ab3787d13fe235bdb729b4f35060159ae40e3cec8b01ddf8ab05759b1061f525633a3b8338cd853a750b723a001e7fb4b692c504d9b5",
                            "timestamp": 1531165245
                        },
                        {
                            "nonce": 10393447810,
                            "pubkey": "f7bec1a681a8f9d00f93d6e84202ff3bc74f2b8e443d3118f32151b82976b7a0be568cc8fa7b8a8ed1963ce14861d63f3d6d06c905b9980223432b921b096ee8",
                            "reference": "38682de32a13ab059f249f1a04f38e7aad6a4d8ec60e9b26351384b2a11b0000",
                            "signature": "bd8cd4762a0cfd74ddfea89a4a2f3e022f9921bd731092ed470355e541fe419717a1d2dbdd9068f058e92e65eb973678faa08027b1b418268e027f20b6c4d5c0",
                            "timestamp": 1531165241
                        }
                    ],
                    "nonce": 59184384829,
                    "prev_tick": "38682de32a13ab059f249f1a04f38e7aad6a4d8ec60e9b26351384b2a11b0000",
                    "pubkey": "79d95d151c5cd9487246d74e0788ebca8aea675b4f2235fb1a68234db43f04004d1b38e8f9fc41c3f88fb8d4e9b1f4909e34b2cb4b599ed72b0ceca3edac198e",
                    "signature": "3ff4e4f37e46f17a78dc83d730723baede36fc3cc4995a18ccddaafceb045f8a66e34520d9ba9c83e02e46d694c078c72cd5dec9e5e70dac1431e242835168de"
                }
            }
        ]

    assert validate_clockchain(example_clockchain)