#!/bin/bash

FOLDER=bin
KEYSTORE=my-release-key.keystore

#################
#### armv7a #####
#################
echo ">>> Building armeabi-v7a architecture..."
APK_V7A_BUILT=$(buildozer android release || exit $?)
APK_V7A_NAME=$(echo "${APK_V7A_BUILT}" | tail -n1 | cut -d' ' -f3)
echo ">>> Built APK: ${APK_V7A_NAME}"

echo ">>> Signing ${APK_V7A_NAME}..."
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore $KEYSTORE "$FOLDER/${APK_V7A_NAME}" alias_name || exit $?

echo ">>> Checking if ${APK_V7A_NAME} is verified..."
jarsigner -verify "$FOLDER/${APK_V7A_NAME}" || exit $?

echo ">>> Running zipalign to create ${APK_V7A_NAME/-unsigned}..."
# remove -unsigned substring from name
zipalign -f 4 "$FOLDER/${APK_V7A_NAME}" "$FOLDER/${APK_V7A_NAME/-unsigned}" || exit $?

#################
### arm64-v8a ###
#################
echo ">>> Building arm64-v8a architecture..."
APK_ARM64_BUILT=$(buildozer --profile armv8 android release || exit $?)
APK_ARM64_NAME=$(echo "${APK_ARM64_BUILT}" | tail -n1 | cut -d' ' -f3)
echo ">>> Built APK: ${APK_ARM64_NAME}"

echo ">>> Signing ${APK_ARM64_NAME}..."
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore $KEYSTORE "$FOLDER/${APK_ARM64_NAME}" alias_name || exit $?

echo ">>> Checking if ${APK_ARM64_NAME} is verified..."
jarsigner -verify "$FOLDER/${APK_ARM64_NAME}" || exit $?

echo ">>> Running zipalign to create ${APK_ARM64_NAME/-unsigned}..."
# remove -unsigned substring from name
zipalign -f 4 "$FOLDER/${APK_ARM64_NAME}" "$FOLDER/${APK_ARM64_NAME/-unsigned}" || exit $?

echo ">>> Cleanup..."
rm "$FOLDER/${APK_V7A_NAME}"
rm "$FOLDER/${APK_ARM64_NAME}"
