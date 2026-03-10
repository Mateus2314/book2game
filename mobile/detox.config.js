module.exports = {
  testRunner: 'jest',
  runnerConfig: 'ios.sim.debug',
  configurations: {
    'ios.sim.debug': {
      device: {
        type: 'ios.simulator',
        device: {
          type: 'iPhone 15',
        },
      },
      app: 'ios.debug',
    },
    'ios.sim.release': {
      device: {
        type: 'ios.simulator',
        device: {
          type: 'iPhone 15',
        },
      },
      app: 'ios.release',
    },
    'android.emu.debug': {
      device: {
        type: 'android.emulator',
        device: {
          avdName: 'Pixel_3_API_30',
        },
      },
      app: 'android.debug',
    },
    'android.emu.release': {
      device: {
        type: 'android.emulator',
        device: {
          avdName: 'Pixel_3_API_30',
        },
      },
      app: 'android.release',
    },
  },
  apps: {
    'ios.debug': {
      type: 'ios.app',
      binaryPath: 'ios/build/Build/Products/Debug-iphonesimulator/book2game.app',
      build: 'xcodebuild -workspace ios/book2game.xcworkspace -scheme book2game -configuration Debug -sdk iphonesimulator -derivedDataPath ios/build'
    },
    'ios.release': {
      type: 'ios.app',
      binaryPath: 'ios/build/Build/Products/Release-iphonesimulator/book2game.app',
      build: 'xcodebuild -workspace ios/book2game.xcworkspace -scheme book2game -configuration Release -sdk iphonesimulator -derivedDataPath ios/build'
    },
    'android.debug': {
      type: 'android.apk',
      binaryPath: 'android/app/build/outputs/apk/debug/app-debug.apk',
      build: 'cd android && ./gradlew assembleDebug assembleAndroidTest -DtestBuildType=debug'
    },
    'android.release': {
      type: 'android.apk',
      binaryPath: 'android/app/build/outputs/apk/release/app-release.apk',
      build: 'cd android && ./gradlew assembleRelease assembleAndroidTest -DtestBuildType=release'
    },
  },
};