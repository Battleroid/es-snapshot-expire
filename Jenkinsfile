node('docker'){
  checkoutRepo()

  stage("Docker Build") {
    buildDocker.standardRun()
  }
}
