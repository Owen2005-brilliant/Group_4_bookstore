### 2.1 集合设计

####  books（全局图书库）
存放从 SQLite (book_lx.db, 约3.4GB) 导入的图书信息。

示例文档：
```json
{
  "id": "27173553",
  "title": "白金数据",
  "author": "[日] 东野圭吾",
  "publisher": "北京联合出版公司",
  "original_title": "プラチナデータ",
  "translator": "赵峥",
  "pub_year": "2018-10",
  "pages": 327,
  "price": 4200,
  "currency_unit": "元",
  "binding": "平装",
  "isbn": "9787559631167",
  "author_intro": "...",
  "book_intro": "...",
  "content": "...",
  "tags": "推理,东野圭吾"
}

商店信息
{
  "store_id": "s1",
  "user_id": "seller_001",
  "store_name": "张三的小书店"
}

store_books（店内售卖的图书）
{
  "store_id": "s1",
  "book_id": "27173553",
  "price": 3500,
  "stock_level": 20,
  "title": "白金数据",
  "author": "[日] 东野圭吾"
}

users（用户钱包信息）
{
  "user_id": "u1",
  "balance": 100000
}


orders（订单表）
{
  "order_id": "d0b7b8f7-5d1c-4a1d-b4b9-3ffc0d0c3e2c",
  "buyer_id": "u1",
  "store_id": "s1",
  "status": "paid",
  "total_price": 7000,
  "created_time": 1730700000,
  "deliver_time": 1730701200,
  "receive_time": 1730703600
}


order_items（订单明细）
{
  "order_id": "d0b7b8f7-5d1c-4a1d-b4b9-3ffc0d0c3e2c",
  "book_id": "27173553",
  "count": 2,
  "price": 3500,
  "title": "白金数据"
}



这个写完基本就秒杀很多人了。

---

## 3. 性能 / 索引 说明（报告段落）

这一段你也可以直接贴进报告“性能与索引设计”：

```markdown
本项目在将 SQLite 数据迁移到 MongoDB 后，对高频访问的集合建立了以下索引，以保证在 4 万+ 图书数据量、订单不断增长的情况下仍然能快速响应：

1. **图书搜索场景**
   - 在 `books` 集合上建立了 `title`、`author` 普通索引，用于前端按书名或作者的模糊查询。
   - 若 MongoDB 版本支持，额外建立了文本索引(`title`, `author`, `book_intro`, `tags`)，用于跨字段的全文搜索。
   - 这样做的原因是图书表是最大的表，且搜索是高频操作。

2. **店内库存读取场景**
   - 在 `store_books` 集合上建立复合唯一索引(`store_id`, `book_id`)，可以在下单时 O(1) 找到某个店铺的某本书的库存和售价，不需要做全表扫描。
   - 同时对 `title` 建索引，支持“只在当前店铺中搜索图书”的扩展需求。

3. **订单查询与状态流转**
   - 在 `orders` 集合上建立 `buyer_id` 索引，用户查询“我的历史订单”时只会扫描自己的订单。
   - 建立 `status` 索引，便于后台或定时任务快速找到“未支付”或“正在配送”的订单进行处理。
   - 建立 `created_time` 索引，为“超时未支付自动取消”提供支撑。

4. **一致性与唯一性保证**
   - 对 `books.id`、`stores.store_id`、`orders.order_id` 建立唯一索引，防止导入或业务并发时产生重复数据。
   - 对 `store_books (store_id, book_id)` 建唯一索引，保证一个店铺同一本书只有一条库存记录，简化了更新库存的逻辑。

总体来说，上述索引都是围绕三类高频操作设计的：**搜索、下单/扣库存、订单查询**，能够显著减少 MongoDB 的扫描范围，提高系统吞吐量。
