const WXAPI = require('../../wxapi/main')
const { buildShoppingList, formatSchedule } = require('../../utils/dinner-plan.js')

Page({
  data: {
    plan: null,
    loading: true,
    submitting: false,
    activeTab: 'menu',
    shoppingList: [],
    missingRecipes: [],
    missingRecipesText: '',
    expandedRecipeItemId: null,
    editing: false,
    editItems: [],
    members: [],
    availableFoods: [],
    filteredFoods: [],
    foodSearch: '',
    foodPickerOpen: false
  },
  onLoad: function(options) {
    this.planId = options && Number(options.id) || null
    if (options && options.tab === 'shopping') this.setData({ activeTab: 'shopping' })
  },
  onShow: function() {
    this.loadPlan()
  },
  onPullDownRefresh: function() {
    this.loadPlan().finally(() => wx.stopPullDownRefresh())
  },
  loadPlan: function() {
    this.setData({ loading: true })
    const request = this.planId ? WXAPI.getDinnerPlan(this.planId) : WXAPI.dinnerPlanCurrent()
    return request.then(res => {
      if (res.code === 0) {
        const plan = res.data && res.data.id && res.data.status === 'pending' ? res.data : null
        if (plan) {
          plan.feeding_total = (plan.items || []).reduce((sum, item) => sum + Number(item.feeding_value || 0) * Number(item.quantity || 0), 0)
          plan.items = (plan.items || []).map(item => Object.assign({}, item, {
            cook_reward: Number(item.feeding_value || 0) * Number(item.quantity || 0)
          }))
          plan.schedule_text = formatSchedule(plan.scheduled_for)
        }
        const shopping = buildShoppingList(plan ? plan.items : [])
        this.setData({ plan, shoppingList: shopping.items, missingRecipes: shopping.missingRecipes, missingRecipesText: shopping.missingRecipes.join('、'), expandedRecipeItemId: null })
        if (plan && plan.notification_unread && WXAPI.markDinnerPlanSeen) {
          WXAPI.markDinnerPlanSeen(plan.id).then(marked => {
            if (marked.code === 0 && this.data.plan && this.data.plan.id === plan.id) {
              this.setData({ plan: Object.assign({}, this.data.plan, { notification_unread: false }) })
            }
          }).catch(() => {})
        }
      }
    }).catch(() => {
      wx.showToast({ title: '加载失败，请检查网络', icon: 'none' })
    }).finally(() => this.setData({ loading: false }))
  },
  toggleRecipe: function(e) {
    const itemId = Number(e.currentTarget.dataset.id)
    if (!itemId || !this.data.plan) return
    const item = (this.data.plan.items || []).find(candidate => candidate.id === itemId)
    if (!item || !item.recipe_steps || !item.recipe_steps.length) return
    this.setData({ expandedRecipeItemId: this.data.expandedRecipeItemId === itemId ? null : itemId })
  },
  showMenu: function() {
    this.setData({ activeTab: 'menu' })
  },
  showShoppingList: function() {
    this.setData({ activeTab: 'shopping' })
  },
  beginEdit: function() {
    if (!this.data.plan || this.data.submitting) return
    const editItems = this.data.plan.items.map(item => Object.assign({}, item))
    this.setData({ editing: true, editItems, activeTab: 'menu', foodPickerOpen: false })
    WXAPI.diningGroupCurrent().then(res => {
      if (res.code === 0 && res.data) this.setData({ members: res.data.members || [] })
    }).catch(() => wx.showToast({ title: '饭搭子加载失败', icon: 'none' }))
  },
  cancelEdit: function() {
    this.setData({ editing: false, editItems: [], foodPickerOpen: false, foodSearch: '' })
  },
  changeQuantity: function(e) {
    const index = Number(e.currentTarget.dataset.index)
    const delta = Number(e.currentTarget.dataset.delta)
    const items = this.data.editItems.slice()
    if (!items[index]) return
    const quantity = Math.max(1, Math.min(99, Number(items[index].quantity) + delta))
    items[index] = Object.assign({}, items[index], { quantity })
    this.setData({ editItems: items })
  },
  chooseCook: function(e) {
    const index = Number(e.currentTarget.dataset.index)
    const cookId = Number(e.currentTarget.dataset.userId)
    const member = this.data.members.find(item => item.user_id === cookId)
    const items = this.data.editItems.slice()
    if (!items[index] || !member) return
    items[index] = Object.assign({}, items[index], { cook_user_id: cookId, cook_name: member.nickname })
    this.setData({ editItems: items })
  },
  removeFood: function(e) {
    const index = Number(e.currentTarget.dataset.index)
    const items = this.data.editItems.slice()
    items.splice(index, 1)
    this.setData({ editItems: items })
  },
  loadFoods: function(page, accumulated) {
    return WXAPI.foods({ page, page_size: 100 }).then(res => {
      if (res.code !== 0) throw new Error(res.message || '菜单加载失败')
      const foods = accumulated.concat(res.data || [])
      return (res.data || []).length < 100 ? foods : this.loadFoods(page + 1, foods)
    })
  },
  openFoodPicker: function() {
    this.setData({ foodPickerOpen: true, foodSearch: '', filteredFoods: this.data.availableFoods })
    if (this.data.availableFoods.length) return Promise.resolve()
    return this.loadFoods(1, []).then(foods => {
      const search = String(this.data.foodSearch || '').trim().toLowerCase()
      this.setData({ availableFoods: foods, filteredFoods: foods.filter(food => food.name.toLowerCase().indexOf(search) >= 0) })
    })
      .catch(() => wx.showToast({ title: '菜单加载失败', icon: 'none' }))
  },
  closeFoodPicker: function() {
    this.setData({ foodPickerOpen: false })
  },
  noop: function() {},
  searchFoods: function(e) {
    const search = String(e.detail.value || '').trim().toLowerCase()
    this.setData({
      foodSearch: e.detail.value,
      filteredFoods: this.data.availableFoods.filter(food => food.name.toLowerCase().indexOf(search) >= 0)
    })
  },
  addFood: function(e) {
    const foodId = Number(e.currentTarget.dataset.id)
    const food = this.data.availableFoods.find(item => item.id === foodId)
    if (!food) return
    const items = this.data.editItems.slice()
    if (items.some(item => item.food_id === foodId)) {
      wx.showToast({ title: '这道菜已在菜单中，可调整份数', icon: 'none' })
      return
    }
    if (items.length >= 30) {
      wx.showToast({ title: '一份菜单最多 30 道菜', icon: 'none' })
      return
    }
    items.push({ food_id: foodId, food_name: food.name, food_image_url: food.pic,
      feeding_value: food.feeding_value, quantity: 1, cook_user_id: null, cook_name: '' })
    this.setData({ editItems: items, foodPickerOpen: false })
  },
  saveEdit: function() {
    if (this.data.submitting || !this.data.plan) return
    const items = this.data.editItems
    if (!items.length) {
      wx.showToast({ title: '至少保留一道菜', icon: 'none' })
      return
    }
    if (items.some(item => !item.cook_user_id)) {
      wx.showToast({ title: '请给每道菜选做菜人', icon: 'none' })
      return
    }
    this.setData({ submitting: true })
    const payload = { items: items.map(item => ({
      food_id: item.food_id, quantity: item.quantity, cook_user_id: item.cook_user_id
    })) }
    return WXAPI.updateDinnerPlan(this.data.plan.id, payload).then(res => {
      if (res.code === 0) {
        this.cancelEdit()
        wx.showToast({ title: '菜单已更新', icon: 'success' })
        return this.loadPlan()
      }
    }).catch(() => wx.showToast({ title: '保存失败，请检查网络', icon: 'none' }))
      .finally(() => this.setData({ submitting: false }))
  },
  completePlan: function() {
    this.updatePlan('completeDinnerPlan', '这顿饭已记录')
  },
  cancelPlan: function() {
    this.updatePlan('cancelDinnerPlan', '菜单已取消')
  },
  updatePlan: function(method, message) {
    if (!this.data.plan || this.data.submitting) {
      return
    }
    this.setData({ submitting: true })
    WXAPI[method](this.data.plan.id).then(res => {
      if (res.code === 0) {
        if (method === 'completeDinnerPlan') {
          const value = this.data.plan.feeding_total || 0
          wx.showToast({ title: '已记录 +' + value + ' 投喂值', icon: 'success' })
        }
        this.setData({ plan: null })
        if (method !== 'completeDinnerPlan') wx.showToast({ title: message, icon: 'success' })
      }
    }).catch(() => {
      wx.showToast({ title: '操作失败，请检查网络', icon: 'none' })
    }).finally(() => this.setData({ submitting: false }))
  },
  goChoose: function() {
    wx.switchTab({ url: '/pages/category/category' })
  }
})
