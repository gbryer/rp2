# Copyright 2021 eprbell
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import unittest

from dateutil.tz import tzutc

from configuration import Configuration
from entry_types import TransactionType
from in_transaction import InTransaction
from out_transaction import OutTransaction
from rp2_error import RP2TypeError, RP2ValueError


class TestInTransaction(unittest.TestCase):
    _configuration: Configuration

    @classmethod
    def setUpClass(cls) -> None:
        TestInTransaction._configuration = Configuration("./config/test_data.config")

    def setUp(self) -> None:
        self.maxDiff = None

    def test_transaction_type(self) -> None:
        self.assertEqual(TransactionType.BUY, TransactionType.type_check_from_string("transaction_type", "buy"))
        self.assertEqual(TransactionType.DONATE, TransactionType.type_check_from_string("transaction_type", "dOnAtE"))
        self.assertEqual(TransactionType.EARN, TransactionType.type_check_from_string("transaction_type", "Earn"))
        self.assertEqual(TransactionType.GIFT, TransactionType.type_check_from_string("transaction_type", "GIFT"))
        self.assertEqual(TransactionType.MOVE, TransactionType.type_check_from_string("transaction_type", "MoVe"))
        self.assertEqual(TransactionType.SELL, TransactionType.type_check_from_string("transaction_type", "sell"))

        with self.assertRaisesRegex(RP2TypeError, "Parameter name is not a string: .*"):
            TransactionType.type_check_from_string(12, "buy")  # type: ignore
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'transaction_type' has non-string value .*"):
            TransactionType.type_check_from_string("transaction_type", 34.6)  # type: ignore
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'transaction_type' has non-string value .*"):
            TransactionType.type_check_from_string("transaction_type", None)  # type: ignore
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'transaction_type' has invalid transaction type value: .*"):
            TransactionType.type_check_from_string("transaction_type", "Cook")

    def test_taxable_in_transaction(self) -> None:
        in_transaction: InTransaction = InTransaction(
            self._configuration,
            19,
            "2021-01-02T08:42:43.882Z",
            "B1",
            "BlockFi",
            "Bob",
            "eaRn",
            1000.0,
            2.0002,
            0,
            2000.2,
            2000.2,
        )

        InTransaction.type_check("my_instance", in_transaction)
        self.assertTrue(in_transaction.is_taxable())
        self.assertEqual(2000.2, in_transaction.usd_taxable_amount)
        self.assertEqual(19, in_transaction.line)
        self.assertEqual(2021, in_transaction.timestamp.year)
        self.assertEqual(1, in_transaction.timestamp.month)
        self.assertEqual(2, in_transaction.timestamp.day)
        self.assertEqual(8, in_transaction.timestamp.hour)
        self.assertEqual(42, in_transaction.timestamp.minute)
        self.assertEqual(43, in_transaction.timestamp.second)
        self.assertEqual(882000, in_transaction.timestamp.microsecond)
        self.assertEqual(tzutc(), in_transaction.timestamp.tzinfo)
        self.assertEqual("B1", in_transaction.asset)
        self.assertEqual("BlockFi", in_transaction.exchange)
        self.assertEqual("Bob", in_transaction.holder)
        self.assertEqual(TransactionType.EARN, in_transaction.transaction_type)
        self.assertEqual(1000, in_transaction.spot_price)
        self.assertEqual(2.0002, in_transaction.crypto_in)
        self.assertEqual(2000.2, in_transaction.usd_in_no_fee)
        self.assertEqual(2000.2, in_transaction.usd_in_with_fee)
        self.assertEqual(0, in_transaction.usd_fee)
        self.assertEqual(2.0002, in_transaction.crypto_balance_change)
        self.assertEqual(2000.2, in_transaction.usd_balance_change)

        self.assertEqual(
            str(in_transaction),
            """InTransaction:
  line=19
  timestamp=2021-01-02 08:42:43.882000 +0000
  asset=B1
  exchange=BlockFi
  holder=Bob
  transaction_type=TransactionType.EARN
  spot_price=1000.0000
  crypto_in=2.00020000
  usd_fee=0.0000
  usd_in_no_fee=2000.2000
  usd_in_with_fee=2000.2000
  is_taxable=True
  usd_taxable_amount=2000.2000""",
        )
        self.assertEqual(
            in_transaction.to_string(2, repr_format=False, extra_data=["foobar", "qwerty"]),
            """    InTransaction:
      line=19
      timestamp=2021-01-02 08:42:43.882000 +0000
      asset=B1
      exchange=BlockFi
      holder=Bob
      transaction_type=TransactionType.EARN
      spot_price=1000.0000
      crypto_in=2.00020000
      usd_fee=0.0000
      usd_in_no_fee=2000.2000
      usd_in_with_fee=2000.2000
      is_taxable=True
      usd_taxable_amount=2000.2000
      foobar
      qwerty""",
        )
        self.assertEqual(
            in_transaction.to_string(2, repr_format=True, extra_data=["foobar", "qwerty"]),
            (
                "    InTransaction("
                "line=19, "
                "timestamp='2021-01-02 08:42:43.882000 +0000', "
                "asset='B1', "
                "exchange='BlockFi', "
                "holder='Bob', "
                "transaction_type=<TransactionType.EARN: 'earn'>, "
                "spot_price=1000.0000, "
                "crypto_in=2.00020000, "
                "usd_fee=0.0000, "
                "usd_in_no_fee=2000.2000, "
                "usd_in_with_fee=2000.2000, "
                "is_taxable=True, "
                "usd_taxable_amount=2000.2000, "
                "foobar, "
                "qwerty)"
            ),
        )

    def test_non_taxable_in_transaction(self) -> None:
        in_transaction = InTransaction(
            self._configuration,
            19,
            "1841-01-02T15:22:03Z",
            "B2",
            "Coinbase",
            "Alice",
            "BuY",
            1000,
            2.0002,
            20,
        )
        self.assertFalse(in_transaction.is_taxable())
        self.assertEqual(in_transaction.usd_taxable_amount, 0)
        self.assertEqual("B2", in_transaction.asset)
        self.assertEqual(TransactionType.BUY, in_transaction.transaction_type)
        self.assertEqual(2.0002, in_transaction.crypto_balance_change)
        self.assertEqual(2020.2, in_transaction.usd_balance_change)

        self.assertEqual(
            str(in_transaction),
            """InTransaction:
  line=19
  timestamp=1841-01-02 15:22:03.000000 +0000
  asset=B2
  exchange=Coinbase
  holder=Alice
  transaction_type=TransactionType.BUY
  spot_price=1000.0000
  crypto_in=2.00020000
  usd_fee=20.0000
  usd_in_no_fee=2000.2000
  usd_in_with_fee=2020.2000
  is_taxable=False
  usd_taxable_amount=0.0000""",
        )

    def test_bad_to_string(self) -> None:
        in_transaction: InTransaction = InTransaction(
            self._configuration,
            19,
            "2021-01-02T08:42:43.882Z",
            "B1",
            "BlockFi",
            "Bob",
            "eaRn",
            1000.0,
            2.0002,
            0,
            2000.2,
            2000.2,
        )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'indent' has non-integer value"):
            in_transaction.to_string(None, repr_format=False, extra_data=["foobar", "qwerty"])  # type: ignore
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'indent' has non-positive value.*"):
            in_transaction.to_string(-1, repr_format=False, extra_data=["foobar", "qwerty"])
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'repr_format' has non-bool value .*"):
            in_transaction.to_string(1, repr_format="False", extra_data=["foobar", "qwerty"])  # type: ignore
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'extra_data' is not of type List"):
            in_transaction.to_string(1, repr_format=False, extra_data="foobar")  # type: ignore

    def test_bad_in_transaction(self) -> None:
        with self.assertRaisesRegex(RP2TypeError, "Parameter name is not a string:.*"):
            InTransaction.type_check(None, None)  # type: ignore
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'my_instance' is not of type InTransaction:.*"):
            InTransaction.type_check("my_instance", None)  # type: ignore
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'my_instance' is not of type InTransaction: OutTransaction"):
            InTransaction.type_check(
                "my_instance", OutTransaction(self._configuration, 45, "2021-01-12T11:51:38Z", "B1", "BlockFi", "Bob", "SELL", 10000, 1, 0)
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'configuration' is not of type Configuration: .*"):
            # Bad configuration
            InTransaction(
                None,  # type: ignore
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'configuration' is not of type Configuration: .*"):
            # Bad configuration
            InTransaction(
                "config",  # type: ignore
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "EARN",
                1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'line' has non-positive value .*"):
            # Bad line
            InTransaction(
                self._configuration,
                -19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "Earn",
                1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'line' has non-integer .*"):
            # Bad line
            InTransaction(
                self._configuration,
                "19",  # type: ignore
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "buy",
                1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2ValueError, "Error parsing parameter 'timestamp': Unknown string format: .*"):
            # Bad timestamp
            InTransaction(
                self._configuration,
                19,
                "abcdefg",
                "B1",
                "BlockFi",
                "Bob",
                "BUY",
                1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'timestamp' value has no timezone info: .*"):
            # Bad timestamp
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43",
                "B1",
                "BlockFi",
                "Bob",
                "eARn",
                1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'timestamp' has non-string value .*"):
            # Bad timestamp
            InTransaction(
                self._configuration,
                19,
                1111,  # type: ignore
                "B1",
                "BlockFi",
                "Bob",
                "EaRn",
                1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'asset' value is not known: .*"):
            # Bad asset
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "yyy",
                "BlockFi",
                "Bob",
                "eArN",
                1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'asset' has non-string value .*"):
            # Bad asset
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                1111,  # type: ignore
                "BlockFi",
                "Bob",
                "eaRn",
                1000.0,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'exchange' value is not known: .*"):
            # Bad exchange
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "blockfi",
                "Bob",
                "eaRn",
                1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'exchange' has non-string value .*"):
            # Bad exchange
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                1111,  # type: ignore
                "Bob",
                "eaRn",
                1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'holder' value is not known: .*"):
            # Bad holder
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "qwerty",
                "eaRn",
                1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'holder' has non-string value .*"):
            # Bad holder
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                1111,  # type: ignore
                "eaRn",
                1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2ValueError, ".*InTransaction at line.*invalid transaction type.*"):
            # Bad transaction type
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "seLl",
                1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'transaction_type' has invalid transaction type value: .*"):
            # Bad transaction type
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "",
                1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter .* has invalid transaction type value: .*"):
            # Bad transaction type
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "cook",
                1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter .* has non-string value .*"):
            # Bad transaction type
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                1111,  # type: ignore
                1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2ValueError, ".*InTransaction at line.*parameter 'spot_price' cannot be 0"):
            # Bad spot price
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                0,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'spot_price' has non-positive value .*"):
            # Bad spot price
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                -1000,
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'spot_price' has non-numeric value .*"):
            # Bad spot price
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                "1000",  # type: ignore
                2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'crypto_in' has zero value"):
            # Bad crypto in
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                1000,
                0,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'crypto_in' has non-positive value .*"):
            # Bad crypto in
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                1000,
                -2.0002,
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'crypto_in' has non-numeric value .*"):
            # Bad crypto in
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                1000.0,
                "2.0002",  # type: ignore
                20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'usd_fee' has non-positive value .*"):
            # Bad usd fee
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                1000,
                2.0002,
                -20,
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'usd_fee' has non-numeric value .*"):
            # Bad usd fee
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                1000,
                2.0002,
                "20",  # type: ignore
                2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'usd_in_no_fee' has non-positive value .*"):
            # Bad usd in no fee
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                1000,
                2.0002,
                20,
                -2000.2,
                2020.2,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'usd_in_no_fee' has non-numeric value .*"):
            # Bad usd in no fee
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                1000.0,
                2.0002,
                20,
                "2000.2",  # type: ignore
                2020.2,
            )
        with self.assertRaisesRegex(RP2ValueError, "Parameter 'usd_in_with_fee' has non-positive value .*"):
            # Bad usd in with fee
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                1000,
                2.0002,
                20,
                2000.2,
                -2020.2,
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'usd_in_with_fee' has non-numeric value .*"):
            # Bad usd in with fee
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                1000,
                2.0002,
                20,
                2000.2,
                (1, 2, 3),  # type: ignore
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'notes' has non-string value .*"):
            # Bad notes
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                1000.0,
                2.0002,
                20,
                2000.2,
                2020.2,
                35.6,  # type: ignore
            )
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'notes' has non-string value .*"):
            # Bad notes
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                1000.0,
                2.0002,
                20,
                2000.2,
                2020.2,
                notes=[1, 2, 3],  # type: ignore
            )

        with self.assertLogs(level="WARNING") as log:
            # Crypto in * spot price != USD in (without fee)
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                1000,
                2.0002,
                1000,
                1900.2,
                2000.2,
            )
            self.assertTrue(re.search(".* InTransaction at line.*crypto_in.*spot_price != usd_in_no_fee:.*", log.output[0]))  # type: ignore

        with self.assertLogs(level="WARNING") as log:
            # USD in (with fee) != USD in (without fee) + USD fee
            InTransaction(
                self._configuration,
                19,
                "2021-01-02T08:42:43.882Z",
                "B1",
                "BlockFi",
                "Bob",
                "eaRn",
                1000,
                2.0002,
                18,
                2000.2,
                2020.2,
            )
            self.assertTrue(re.search(".* InTransaction at line.*usd_in_with_fee != usd_in_no_fee.*usd_fee:.*", log.output[0]))  # type: ignore


if __name__ == "__main__":
    unittest.main()