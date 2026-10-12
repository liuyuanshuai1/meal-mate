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
    expandedRecipeItemId: null
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
