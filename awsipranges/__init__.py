"""Work with AWS IP address ranges in native Python."""

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from awsipranges.data_loading import get_ranges  # noqa: F401
from awsipranges.exceptions import AWSIPRangesException, HTTPError  # noqa: F401
from awsipranges.models.awsipprefix import (  # noqa: F401
    AWSIPPrefix,
    AWSIPv4Prefix,
    AWSIPv6Prefix,
)
from awsipranges.models.awsipprefixes import AWSIPPrefixes  # noqa: F401
