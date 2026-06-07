# frontend-category

目标：菜单页按分类浏览所有可选菜品，复用现有左右联动结构。

## 最小任务

- [ ] 修改 `pages/category/category.js`，加载 `WXAPI.foodCategories()`
- [ ] 修改 `pages/category/category.js`，加载 `WXAPI.foods({ page: 1, page_size: 1000 })`
- [ ] 按 `categoryId` 将菜品组装到现有 `goodsWrap`
- [ ] 分类结构包含 `id`、`name`、`sort`、`scrollId`
- [ ] 菜品结构包含 `id`、`categoryId`、`name`、`pic`、`minPrice`
- [ ] 保留点击左侧分类滚动右侧列表能力
- [ ] 保留右侧滚动同步左侧选中能力
- [ ] 点击菜品进入 `/pages/goods-details/index?id=xxx`
- [ ] 分类为空时展示空状态
- [ ] 某分类菜品为空时不渲染空分组或展示轻量空提示
- [ ] 文案中将“商品”替换为“菜品”

## 验收

- [ ] 菜单页能展示后端分类和菜品
- [ ] 分类切换、滚动同步、详情跳转均可用
- [ ] 第一版不需要在列表直接加入今晚菜单
