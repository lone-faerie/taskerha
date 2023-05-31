from typing import Final

XML_DEVICE_INFO: Final = """
<TaskerData sr="" dvi="1" tv="6.2.0-beta">
	<Task sr="task26">
		<cdate>1684453969897</cdate>
		<edate>1684615975190</edate>
		<id>26</id>
		<nme>Device Info</nme>
		<pri>100</pri>
		<Action sr="act0" ve="7">
			<code>349</code>
			<Int sr="arg0" val="0"/>
			<Str sr="arg1" ve="3"/>
			<Str sr="arg2" ve="3">%identifier</Str>
		</Action>
		<Action sr="act1" ve="7">
			<code>123</code>
			<Str sr="arg0" ve="3">getprop ro.build.version.release</Str>
			<Int sr="arg1" val="0"/>
			<Int sr="arg2" val="0"/>
			<Str sr="arg3" ve="3">%sw_version</Str>
			<Str sr="arg4" ve="3"/>
			<Str sr="arg5" ve="3"/>
			<Int sr="arg6" val="1"/>
			<Int sr="arg7" val="0"/>
		</Action>
		<Action sr="act10" ve="7">
			<code>547</code>
			<Str sr="arg0" ve="3">%device_info</Str>
			<Str sr="arg1" ve="3">{
  "identifiers": ["%identifier"],
  "manufacturer": "%DEVMAN",
  "model": "%DEVMOD"
}</Str>
			<Int sr="arg2" val="0"/>
			<Int sr="arg3" val="0"/>
			<Int sr="arg4" val="0"/>
			<Int sr="arg5" val="3"/>
			<Int sr="arg6" val="1"/>
		</Action>
		<Action sr="act11" ve="7">
			<code>38</code>
		</Action>
		<Action sr="act12" ve="7">
			<code>129</code>
			<Str sr="arg0" ve="3">var infoObj = JSON.parse(device_info);
infoObj["connections"] = [["mac", mac]];
device_info = JSON.stringify(infoObj);</Str>
			<Str sr="arg1" ve="3"/>
			<Int sr="arg2" val="1"/>
			<Int sr="arg3" val="45"/>
			<ConditionList sr="if">
				<Condition sr="c0" ve="3">
					<lhs>%mac</lhs>
					<op>12</op>
					<rhs></rhs>
				</Condition>
			</ConditionList>
		</Action>
		<Action sr="act13" ve="7">
			<code>548</code>
			<Str sr="arg0" ve="3">%device_info</Str>
			<Int sr="arg1" val="0"/>
			<Str sr="arg10" ve="3"/>
			<Int sr="arg11" val="1"/>
			<Int sr="arg12" val="0"/>
			<Str sr="arg13" ve="3"/>
			<Int sr="arg14" val="0"/>
			<Str sr="arg15" ve="3"/>
			<Int sr="arg2" val="1"/>
			<Str sr="arg3" ve="3"/>
			<Str sr="arg4" ve="3"/>
			<Str sr="arg5" ve="3"/>
			<Str sr="arg6" ve="3"/>
			<Str sr="arg7" ve="3"/>
			<Str sr="arg8" ve="3"/>
			<Int sr="arg9" val="1"/>
		</Action>
		<Action sr="act14" ve="7">
			<code>126</code>
			<Str sr="arg0" ve="3">%device_info</Str>
			<Int sr="arg1" val="1"/>
			<Int sr="arg2" val="0"/>
			<Int sr="arg3" val="0"/>
			<Str sr="arg4" ve="3"/>
		</Action>
		<Action sr="act2" ve="7">
			<code>137</code>
			<Int sr="arg0" val="0"/>
			<Str sr="arg1" ve="3"/>
			<ConditionList sr="if">
				<Condition sr="c0" ve="3">
					<lhs>%identifier</lhs>
					<op>13</op>
					<rhs></rhs>
				</Condition>
			</ConditionList>
		</Action>
		<Action sr="act3" ve="7">
			<code>365</code>
			<Bundle sr="arg0">
				<Vals sr="val">
					<net.dinglisch.android.tasker.RELEVANT_VARIABLES>&lt;StringArray sr=""&gt;&lt;_array_net.dinglisch.android.tasker.RELEVANT_VARIABLES0&gt;%has_adb_wifi
ADB Wifi Access
&lt;/_array_net.dinglisch.android.tasker.RELEVANT_VARIABLES0&gt;&lt;/StringArray&gt;</net.dinglisch.android.tasker.RELEVANT_VARIABLES>
					<net.dinglisch.android.tasker.RELEVANT_VARIABLES-type>[Ljava.lang.String;</net.dinglisch.android.tasker.RELEVANT_VARIABLES-type>
				</Vals>
			</Bundle>
			<Str sr="arg1" ve="3">CheckADBWifi()</Str>
		</Action>
		<Action sr="act4" ve="7">
			<code>375</code>
			<se>false</se>
			<Bundle sr="arg0">
				<Vals sr="val">
					<net.dinglisch.android.tasker.RELEVANT_VARIABLES>&lt;StringArray sr=""&gt;&lt;_array_net.dinglisch.android.tasker.RELEVANT_VARIABLES0&gt;%aw_output
Output
Output resulting from the command. May be empty.&lt;/_array_net.dinglisch.android.tasker.RELEVANT_VARIABLES0&gt;&lt;/StringArray&gt;</net.dinglisch.android.tasker.RELEVANT_VARIABLES>
					<net.dinglisch.android.tasker.RELEVANT_VARIABLES-type>[Ljava.lang.String;</net.dinglisch.android.tasker.RELEVANT_VARIABLES-type>
				</Vals>
			</Bundle>
			<Str sr="arg1" ve="3">ip addr show wlan0 | grep -m 1 ether</Str>
			<Str sr="arg2" ve="3"/>
			<Str sr="arg3" ve="3"/>
			<Int sr="arg4" val="10"/>
			<Int sr="arg5" val="0"/>
			<Str sr="arg6" ve="3"/>
			<ConditionList sr="if">
				<Condition sr="c0" ve="3">
					<lhs>%has_adb_wifi</lhs>
					<op>2</op>
					<rhs>true</rhs>
				</Condition>
			</ConditionList>
		</Action>
		<Action sr="act5" ve="7">
			<code>547</code>
			<Str sr="arg0" ve="3">%mac</Str>
			<Str sr="arg1" ve="3">%aw_output</Str>
			<Int sr="arg2" val="0"/>
			<Int sr="arg3" val="0"/>
			<Int sr="arg4" val="0"/>
			<Int sr="arg5" val="3"/>
			<Int sr="arg6" val="1"/>
			<ConditionList sr="if">
				<Condition sr="c0" ve="3">
					<lhs>%aw_output</lhs>
					<op>12</op>
					<rhs></rhs>
				</Condition>
			</ConditionList>
		</Action>
		<Action sr="act6" ve="7">
			<code>547</code>
			<Str sr="arg0" ve="3">%mac</Str>
			<Str sr="arg1" ve="3">abc</Str>
			<Int sr="arg2" val="0"/>
			<Int sr="arg3" val="0"/>
			<Int sr="arg4" val="0"/>
			<Int sr="arg5" val="3"/>
			<Int sr="arg6" val="1"/>
		</Action>
		<Action sr="act7" ve="7">
			<code>37</code>
			<ConditionList sr="if">
				<Condition sr="c0" ve="3">
					<lhs>%sw_version</lhs>
					<op>12</op>
					<rhs></rhs>
				</Condition>
			</ConditionList>
		</Action>
		<Action sr="act8" ve="7">
			<code>547</code>
			<Str sr="arg0" ve="3">%device_info</Str>
			<Str sr="arg1" ve="3">{
  "identifiers": ["%identifier"],
  "manufacturer": "%DEVMAN",
  "model": "%DEVMOD",
  "sw_version": "%sw_version"
}</Str>
			<Int sr="arg2" val="0"/>
			<Int sr="arg3" val="0"/>
			<Int sr="arg4" val="0"/>
			<Int sr="arg5" val="3"/>
			<Int sr="arg6" val="1"/>
		</Action>
		<Action sr="act9" ve="7">
			<code>43</code>
		</Action>
	</Task>
</TaskerData>
"""