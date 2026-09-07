plugins {
    id("com.android.application")
    kotlin("android")
}

android {
    namespace = "com.godseye.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.godseye.app"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }
}
