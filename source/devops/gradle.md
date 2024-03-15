## 入门

- Groovy\DSL
- projects/tasks
- build.gradle
- 工程文件.gradle
  - baseline.gradle
  - build.gradle
  - deploy.gradle
  - gradlew
  - jmh.gradle
  - setting.gradle
  - tasks.gradle
  - gradle.properties
```groovy
task hello {
    println 'Hello world!'
}
task upper << {
    String someString = 'mY_nAmE'
    println "Original: " + someString
    println "Upper case: " + someString.toUpperCase()
}
// 任务依赖
task hello << {
    println 'Hello world!'
}
task intro(dependsOn: hello) << {
    println "I'm Gradle"
}
//延迟依赖
task taskX(dependsOn: 'taskY') << {
    println 'taskX'
}
task taskY << {
    println 'taskY'
}
//创建动态任务
4.times { counter ->
    task "task$counter" << {
        println "I'm task number $counter"
    }
}
//api
task hello << {
    println 'Hello Earth'
}
hello.doFirst {
    println 'Hello Venus'
}
hello.doLast {
    println 'Hello Mars'
}
hello << {
    println 'Hello Jupiter'
}
//task增加自定义属性
task myTask {
    ext.myProperty = "myValue"
}

task printTaskProperties << {
    println myTask.myProperty
}
//利用antbuilder
task loadfile << {
    def files = file('../antLoadfileResources').listFiles().sort()
    files.each { File file ->
        if (file.isFile()) {
            ant.loadfile(srcFile: file, property: file.name)
            println " *** $file.name ***"
            println "${ant.properties[file.name]}"
        }
    }
}
//方法抽取
task checksum << {
    fileList('../antLoadfileResources').each {File file ->
        ant.checksum(file: file, property: "cs_$file.name")
        println "$file.name Checksum: ${ant.properties["cs_$file.name"]}"
    }
}
task loadfile << {
    fileList('../antLoadfileResources').each {File file ->
        ant.loadfile(srcFile: file, property: file.name)
        println "I'm fond of $file.name"
    }
}
File[] fileList(String dir) {
    file(dir).listFiles({file -> file.isFile() } as FileFilter).sort()
}
//定义默认任务
defaultTasks 'clean', 'run'
//依赖任务的不同输出
task distribution << {
    println "We build the zip with version=$version"
}
task release(dependsOn: 'distribution') << {
    println 'We release now'
}
gradle.taskGraph.whenReady {taskGraph ->
    if (taskGraph.hasTask(release)) {
        version = '1.0'
    } else {
        version = '1.0-SNAPSHOT'
    }
}

```

## Java构建入门

```groovy


apply plugin:'java'
//导入到eclipse
apply plugin: 'eclipse'
//plugins {
//    id 'java'
//}


// manifest
group 'org.example'
version '1.0-SNAPSHOT'
sourceCompatibility = 1.5
jar {
    manifest {
        attributes 'Implementation-Title': 'Gradle Quickstart', 'Implementation-Version': version
    }
}

repositories {
    mavenCentral()
}

dependencies {
    compile group: 'commons-collections', name: 'commons-collections', version: '3.2'
    testCompile group: 'junit', name: 'junit', version: '4.+'

    testImplementation 'org.junit.jupiter:junit-jupiter-api:5.8.1'
    testRuntimeOnly 'org.junit.jupiter:junit-jupiter-engine:5.8.1'
}

test {
    useJUnitPlatform()
    systemProperties 'property': 'value'
}

//发布jar
uploadArchives {
    repositories {
        flatDir {
            dirs 'repos'
        }
    }
}
```

- 多模块配置-settings-gradle
- 公共配置-subprojects
- 工程依赖
dependencies {
    compile project(':shared')
}
- 多项目构建-发布
task dist(type: Zip) {
    dependsOn spiJar
    from 'src/dist'
    into('libs') {
        from spiJar.archivePath
        from configurations.runtime
    }
}
artifacts {
   archives dist
}
## 依赖&发布
依赖：输入
```
apply plugin: 'java'
repositories {
    mavenCentral()
}
dependencies {
    compile group: 'org.hibernate', name: 'hibernate-core', version: '3.6.7.Final'
    testCompile group: 'junit', name: 'junit', version: '4.+'
}
```
依赖范围：
- compile
- runtime
- testCompile
- testRuntime

外部依赖：
```
dependencies {
    compile group: 'org.hibernate', name: 'hibernate-core', version: '3.6.7.Final'
}
dependencies {
    compile 'org.hibernate:hibernate-core:3.6.7.Final'
}
```
仓库：
```
repositories {
    mavenCentral()
}
repositories {
    maven {
        url "http://repo.mycompany.com/maven2"
    }
}
repositories {
    ivy {
        url "http://repo.mycompany.com/repo"
    }
}
repositories {
    ivy {
        // URL can refer to a local directory
        url "../local-repo"
    }
}
```

打包发布：输出
```
uploadArchives {
    repositories {
        ivy {
            credentials {
                username "username"
                password "pw"
            }
            url "http://repo.mycompany.com"
        }
    }
}

apply plugin: 'maven'
uploadArchives {
    repositories {
        mavenDeployer {
            repository(url: "file://localhost/tmp/myRepo/")
        }
    }
}

```

## Groovy
```
apply plugin: 'groovy'
repositories {
    mavenCentral()
}
dependencies {
    compile 'org.codehaus.groovy:groovy-all:2.2.0'
}  
```

## Web开发
```
//打包
apply plugin: 'war'
//启动
apply plugin: 'jetty'
```

## 命令行

![gradle_1](../_static/gradle_1.png)
```bash
gradle dist test
//跳过test
gradle dist -x test
--continue失败继续进行
description = 'The shared API for the application'
gradle -q tasks
gradle -q tasks --all
gradle projects
```





