# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2023-02-03

### Fixed
- 修复无蓝图的api接口blueprint.ctx.desc报错的问题
- 实现_missing_方法，修复枚举基类无法识别枚举值的问题

### Changed
- 请求接口无参数时访问日志中不打印 “args:”

### Added
- 添加types-ujson包
- 自动生成的文档支持识别必须和可选参数
- 枚举基类字段类名称修改，避免重名
- 枚举基类增加to_desc方法列出枚举的所有描述

## [0.2.0] - 2023-01-19

### Changed
- api json序列化改为使用ujson
- 移除部分3.10以上的语法

### Added
- 日志功能优化改进:
  - 实现方式更加简洁优雅
  - 可按照类型去区分
  - 日志增加打印请求ID
- json响应体格式设置为可配置的
- 添加ujson包，移除orjson包
- 读取蓝图上面的 blueprint.ctx.desc 属性来代替name设置中文tag名
- 引入mypy、autoflake等代码检查工具
- 添加配置文件基类

## [0.1.1] - 2022-12-19

### Changed
- pip 首页的文件修改

## [0.1.0] - 2022-12-19

### Added 

- 接口参数校验
- 接口文档生成
- 日志使用`loguru`代替
- 接口异常拦截
- 接口响应统一化

